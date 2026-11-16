export type AgentEvent =
    | { type: 'thought'; content: string }
    | { type: 'tool_call'; tool: string; input: string }
    | { type: 'tool_result'; tool: string; result: string }
    | { type: 'final'; content: string }
    | { type: 'error'; content: string }