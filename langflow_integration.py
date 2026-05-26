import json
import os
from typing import Dict, Any

def get_graph_json(graph) -> Dict[str, Any]:
    nodes = []
    edges = []
    
    if hasattr(graph, 'nodes'):
        for i, (node_name, node) in enumerate(graph.nodes.items()):
            nodes.append({
                "id": i,
                "name": node_name,
                "type": "agent",
                "description": f"Agent: {node_name}"
            })
    
    if hasattr(graph, 'edges'):
        for i, edge in enumerate(graph.edges):
            edges.append({
                "id": i,
                "source": edge[0] if isinstance(edge, tuple) else edge,
                "target": edge[1] if isinstance(edge, tuple) else edge
            })
    
    return {
        "name": "MediAgent LangGraph Flow",
        "description": "Medical multi-agent system with LangGraph",
        "nodes": nodes,
        "edges": edges,
        "structure": {
            "entry_point": "triage",
            "checkpoint": "human_validation",
            "agents": ["triage", "rag", "diagnostic", "human_validation", "prescription", "report"]
        }
    }

def save_graph_for_langflow(graph, output_path: str = "mediagent_graph.json") -> str:
    graph_data = get_graph_json(graph)
    
    langflow_format = {
        "display_name": "MediAgent Medical System",
        "description": "Multi-agent medical assistant with human-in-the-loop",
        "data": {
            "nodes": [],
            "edges": []
        }
    }
    
    for node in graph_data["nodes"]:
        langflow_format["data"]["nodes"].append({
            "id": str(node["id"]),
            "type": node["type"],
            "data": {
                "node_type": node["name"],
                "display_name": node["name"].capitalize(),
                "description": node.get("description", ""),
                "tool_mode": False
            },
            "position": {
                "x": node["id"] * 250,
                "y": 150 if node["id"] % 2 == 0 else 300
            }
        })
    
    for edge in graph_data["edges"]:
        langflow_format["data"]["edges"].append({
            "id": str(edge["id"]),
            "source": str(edge["source"]),
            "target": str(edge["target"])
        })
    
    os.makedirs("exports", exist_ok=True)
    full_path = os.path.join("exports", output_path)
    
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(langflow_format, f, indent=2, ensure_ascii=False)
    
    return full_path

def create_langflow_yaml() -> str:
    yaml_content = """version: "1.0"
name: "MediAgent Flow"
description: "Medical consultation workflow"
flows:
  - name: "medical_consultation"
    description: "Complete medical consultation process"
    steps:
      - name: "triage"
        type: "agent"
        agent: "Triage Agent"
      - name: "rag"
        type: "agent"
        agent: "RAG Agent"
      - name: "diagnostic"
        type: "agent"
        agent: "Diagnostic Agent"
      - name: "human_validation"
        type: "human"
        agent: "Human Validation"
      - name: "prescription"
        type: "agent"
        agent: "Prescription Agent"
      - name: "report"
        type: "agent"
        agent: "Report Agent"
"""
    os.makedirs("exports", exist_ok=True)
    path = os.path.join("exports", "langflow_config.yaml")
    with open(path, "w", encoding="utf-8") as f:
        f.write(yaml_content)
    return path

def get_graph_structure_summary(graph) -> Dict[str, Any]:
    summary = {
        "total_nodes": 0,
        "agents": [],
        "entry_point": None,
        "checkpoints": [],
        "edges_count": 0
    }
    
    if hasattr(graph, 'nodes'):
        summary["total_nodes"] = len(graph.nodes)
        summary["agents"] = list(graph.nodes.keys())
    
    if hasattr(graph, 'builder'):
        if hasattr(graph.builder, 'entry_point'):
            summary["entry_point"] = graph.builder.entry_point
    
    if hasattr(graph, 'checkpointer'):
        summary["checkpoints"] = ["human_validation"]
    
    if hasattr(graph, 'edges'):
        summary["edges_count"] = len(graph.edges)
    
    return summary