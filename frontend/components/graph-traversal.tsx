"use client";

import {
  ArrowLeft,
  ArrowRight,
  ChevronDown,
  ChevronRight,
  GitBranch,
} from "lucide-react";
import { useState } from "react";
import type { GraphNode } from "@/types/query";

const ENTITY_TYPE_COLORS: Record<string, string> = {
  Policy: "bg-blue-500/10 border-blue-500/30 text-blue-300",
  Department: "bg-purple-500/10 border-purple-500/30 text-purple-300",
  Role: "bg-green-500/10 border-green-500/30 text-green-300",
  Benefit: "bg-amber-500/10 border-amber-500/30 text-amber-300",
  Requirement: "bg-red-500/10 border-red-500/30 text-red-300",
  Process: "bg-cyan-500/10 border-cyan-500/30 text-cyan-300",
  Section: "bg-indigo-500/10 border-indigo-500/30 text-indigo-300",
  Document: "bg-rose-500/10 border-rose-500/30 text-rose-300",
  Unknown: "bg-white/5 border-white/10 text-white/50",
};

function EntityBadge({ type, name }: { type: string; name: string }) {
  const color = ENTITY_TYPE_COLORS[type] ?? ENTITY_TYPE_COLORS.Unknown;
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-md border text-xs font-medium ${color}`}
    >
      {name}
    </span>
  );
}

function GraphNodeRow({ node }: { node: GraphNode }) {
  const [expanded, setExpanded] = useState(false);
  const hasNeighbors = node.neighbors.length > 0;

  return (
    <div className="space-y-1">
      {/* Node header */}
      <button
        type="button"
        onClick={() => hasNeighbors && setExpanded(!expanded)}
        className={`
          w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left
          bg-white/5 border border-white/10
          ${hasNeighbors ? "hover:bg-white/8 cursor-pointer" : "cursor-default"}
          transition-colors duration-150
        `}
      >
        {/* Expand toggle */}
        <div className="shrink-0 text-white/40">
          {hasNeighbors ? (
            expanded ? (
              <ChevronDown className="h-3.5 w-3.5" />
            ) : (
              <ChevronRight className="h-3.5 w-3.5" />
            )
          ) : (
            <div className="w-3.5" />
          )}
        </div>

        {/* Matched node */}
        <EntityBadge type={node.entity_type} name={node.name} />

        {/* Query entity that triggered this match (if different) */}
        {node.query_entity !== node.name && (
          <span className="text-xs text-white/30 italic truncate">
            via "{node.query_entity}"
          </span>
        )}

        {/* Chunk count */}
        <span className="ml-auto text-xs text-white/30 shrink-0">
          {node.chunk_indices.length} chunk
          {node.chunk_indices.length !== 1 ? "s" : ""}
        </span>
      </button>

      {/* Neighbors (expanded) */}
      {expanded && hasNeighbors && (
        <div className="ml-5 space-y-1 border-l border-white/10 pl-3">
          {node.neighbors.map((neighbor, idx) => (
            <div
              // biome-ignore lint/suspicious/noArrayIndexKey: change to another id
              key={idx}
              className="flex items-center gap-2 px-2 py-1.5 rounded-md bg-white/3 text-xs"
            >
              {/* Direction arrow */}
              {neighbor.direction === "outgoing" ? (
                <ArrowRight className="h-3 w-3 text-white/40 shrink-0" />
              ) : (
                <ArrowLeft className="h-3 w-3 text-white/40 shrink-0" />
              )}

              {/* Relation label */}
              <span className="text-white/40 font-mono shrink-0">
                {neighbor.relation}
              </span>

              {/* Neighbor name */}
              <span className="text-white/60 truncate">{neighbor.name}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

interface GraphTraversalProps {
  nodes: GraphNode[];
}

export function GraphTraversal({ nodes }: GraphTraversalProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (!nodes || nodes.length === 0) return null;

  const totalNeighbors = nodes.reduce((sum, n) => sum + n.neighbors.length, 0);

  return (
    <div className="w-full space-y-1.5">
      {/* Collapsible header */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center cursor-pointer gap-2 px-1 text-xs text-white/70 hover:text-white/90 transition-colors duration-150 group"
      >
        <GitBranch className="h-3.5 w-3.5" />
        <span className="font-medium">Graph traversal</span>
        <span className="text-white/50">
          {nodes.length} node{nodes.length !== 1 ? "s" : ""}, {totalNeighbors}{" "}
          connection{totalNeighbors !== 1 ? "s" : ""}
        </span>
        {isOpen ? (
          <ChevronDown className="h-3 w-3 ml-auto" />
        ) : (
          <ChevronRight className="h-3 w-3 ml-auto" />
        )}
      </button>

      {/* Expanded content */}
      {isOpen && (
        <div className="space-y-1.5 animate-in fade-in duration-200">
          {nodes.map((node, idx) => (
            // biome-ignore lint/suspicious/noArrayIndexKey: change to something not array index
            <GraphNodeRow key={idx} node={node} />
          ))}
        </div>
      )}
    </div>
  );
}
