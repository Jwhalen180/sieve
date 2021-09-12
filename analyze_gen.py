from analyze_util import *
import json
from typing import List
import yaml
import copy
import os
import controllers
import analyze_event
import json
import sieve_config
from common import sieve_modes


def delete_only_filtering_pass(causality_edges: List[CausalityEdge]):
    print("Running optional pass: delete-only-filtering ...")
    candidate_edges = []
    for edge in causality_edges:
        if edge.source.is_event() and edge.sink.is_side_effect():
            if edge.sink.content.etype == "Delete":
                candidate_edges.append(edge)
    return candidate_edges


def delete_then_recreate_filtering_pass(causality_edges: List[CausalityEdge], event_key_map):
    print("Running optional pass: delete-then-recreate-filtering ...")
    # this should only be applied to time travel mode
    candidate_edges = []
    for edge in causality_edges:
        side_effect = edge.sink.content
        # time travel only cares about delete for now
        assert side_effect.etype == "Delete"
        keep_this_pair = False
        if side_effect.key in event_key_map:
            for event in event_key_map[side_effect.key]:
                if event.start_timestamp <= side_effect.end_timestamp:
                    continue
                if event.etype == "Added":
                    keep_this_pair = True
        else:
            # if the side effect key never appears in the event_key_map
            # it means the operator does not watch on the resource
            # so we should be cautious and keep this edge
            keep_this_pair = True
        if keep_this_pair:
            candidate_edges.append(edge)
    return candidate_edges


def time_travel_analysis(causality_graph: CausalityGraph, events_data_structure: EventsDataStructure, path: str, project: str, timing="after"):
    causality_edges = causality_graph.get_event_effect_edge_list()
    candidate_edges = delete_only_filtering_pass(causality_edges)
    candidate_edges = delete_then_recreate_filtering_pass(
        candidate_edges, events_data_structure.event_key_map)
    generate_time_travel_yaml(
        candidate_edges, path, project, events_data_structure.event_key_map, timing)


def obs_gap_analysis(causality_graph: CausalityGraph, events_data_structure: EventsDataStructure, path: str, project: str):
    causality_edges = causality_graph.get_event_effect_edge_list()
    candidate_edges = causality_edges
    generate_obs_gap_yaml(
        candidate_edges, path, project, events_data_structure.event_key_map)


def atom_vio_analysis(causality_graph: CausalityGraph, events_data_structure: EventsDataStructure, path: str, project: str):
    causality_edges = causality_graph.get_event_effect_edge_list()
    candidate_edges = causality_edges
    generate_atom_vio_yaml(
        candidate_edges, path, project, events_data_structure.event_key_map)


def generate_time_travel_yaml(causality_edges, path, project, event_key_map, timing):
    yaml_map = {}
    yaml_map["project"] = project
    yaml_map["stage"] = "test"
    yaml_map["mode"] = sieve_modes.TIME_TRAVEL
    yaml_map["straggler"] = sieve_config.config["time_travel_straggler"]
    yaml_map["front-runner"] = sieve_config.config["time_travel_front_runner"]
    yaml_map["operator-pod-label"] = controllers.operator_pod_label[project]
    yaml_map["deployment-name"] = controllers.deployment_name[project]
    yaml_map["timing"] = timing
    suffix = "-b" if timing == "before" else ""
    i = 0
    for edge in causality_edges:
        event = edge.source.content
        side_effect = edge.sink.content
        assert isinstance(event, Event)
        assert isinstance(side_effect, SideEffect)

        prev_event, cur_event = analyze_event.find_previous_event(
            event, event_key_map)
        if prev_event is None:
            continue
        slim_prev_obj, slim_cur_obj = analyze_event.diff_events(
            prev_event, cur_event)
        if len(slim_prev_obj) == 0 and len(slim_cur_obj) == 0:
            continue

        yaml_map["ce-name"] = event.name
        yaml_map["ce-namespace"] = event.namespace
        yaml_map["ce-rtype"] = event.rtype

        yaml_map["ce-diff-current"] = json.dumps(
            analyze_event.canonicalize_event(copy.deepcopy(slim_cur_obj)))
        yaml_map["ce-diff-previous"] = json.dumps(
            analyze_event.canonicalize_event(copy.deepcopy(slim_prev_obj)))
        yaml_map["ce-etype-current"] = cur_event.etype
        yaml_map["ce-etype-previous"] = prev_event.etype

        yaml_map["se-name"] = side_effect.name
        yaml_map["se-namespace"] = side_effect.namespace
        yaml_map["se-rtype"] = side_effect.rtype
        yaml_map["se-etype"] = "ADDED" if side_effect.etype == "Delete" else "DELETED"

        i += 1
        yaml.dump(yaml_map, open(
            os.path.join(path, "time-travel-config-%s%s.yaml" % (str(i), suffix)), "w"), sort_keys=False)
    print("Generated %d time-travel config(s) in %s" % (i, path))


def generate_obs_gap_yaml(causality_edges, path, project, event_key_map):
    yaml_map = {}
    yaml_map["project"] = project
    yaml_map["stage"] = "test"
    yaml_map["mode"] = sieve_modes.OBS_GAP
    yaml_map["operator-pod-label"] = controllers.operator_pod_label[project]
    i = 0
    events_set = set()
    for edge in causality_edges:
        event = edge.source.content
        side_effect = edge.sink.content
        assert isinstance(event, Event)
        assert isinstance(side_effect, SideEffect)

        if event.id not in events_set:
            events_set.add(event.id)
        else:
            continue

        prev_event, cur_event = analyze_event.find_previous_event(
            event, event_key_map)
        if prev_event is None:
            continue
        slim_prev_obj, slim_cur_obj = analyze_event.diff_events(
            prev_event, cur_event)
        if len(slim_prev_obj) == 0 and len(slim_cur_obj) == 0:
            continue

        yaml_map["ce-name"] = event.name
        yaml_map["ce-namespace"] = event.namespace
        yaml_map["ce-rtype"] = event.rtype

        yaml_map["ce-diff-current"] = json.dumps(
            analyze_event.canonicalize_event(copy.deepcopy(slim_cur_obj)))
        yaml_map["ce-diff-previous"] = json.dumps(
            analyze_event.canonicalize_event(copy.deepcopy(slim_prev_obj)))
        yaml_map["ce-etype-current"] = cur_event.etype
        yaml_map["ce-etype-previous"] = prev_event.etype

        i += 1
        yaml.dump(yaml_map, open(
            os.path.join(path, "obs-gap-config-%s.yaml" % (str(i))), "w"), sort_keys=False)
    print("Generated %d obs-gap config(s) in %s" % (i, path))


def generate_atom_vio_yaml(causality_edges, path, project, event_key_map):
    yaml_map = {}
    yaml_map["project"] = project
    yaml_map["stage"] = "test"
    yaml_map["mode"] = sieve_modes.ATOM_VIO
    yaml_map["front-runner"] = sieve_config.config["time_travel_front_runner"]
    yaml_map["operator-pod-label"] = controllers.operator_pod_label[project]
    yaml_map["deployment-name"] = controllers.deployment_name[project]
    i = 0
    for edge in causality_edges:
        event = edge.source.content
        side_effect = edge.sink.content
        assert isinstance(event, Event)
        assert isinstance(side_effect, SideEffect)

        prev_event, cur_event = analyze_event.find_previous_event(
            event, event_key_map)
        if prev_event is None:
            continue
        slim_prev_obj, slim_cur_obj = analyze_event.diff_events(
            prev_event, cur_event)
        if len(slim_prev_obj) == 0 and len(slim_cur_obj) == 0:
            continue

        yaml_map["ce-name"] = event.name
        yaml_map["ce-namespace"] = event.namespace
        yaml_map["ce-rtype"] = event.rtype

        yaml_map["ce-diff-current"] = json.dumps(
            analyze_event.canonicalize_event(copy.deepcopy(slim_cur_obj)))
        yaml_map["ce-diff-previous"] = json.dumps(
            analyze_event.canonicalize_event(copy.deepcopy(slim_prev_obj)))
        yaml_map["ce-etype-current"] = cur_event.etype
        yaml_map["ce-etype-previous"] = prev_event.etype

        yaml_map["se-name"] = side_effect.name
        yaml_map["se-namespace"] = side_effect.namespace
        yaml_map["se-rtype"] = side_effect.rtype
        yaml_map["se-etype"] = side_effect.etype

        # TODO: should find a way to determine crash location
        yaml_map["crash-location"] = "before"
        i += 1
        yaml.dump(yaml_map, open(
            os.path.join(path, "atomic-config-%s.yaml" % (str(i))), "w"), sort_keys=False)
    print("Generated %d atomic config(s) in %s" % (i, path))