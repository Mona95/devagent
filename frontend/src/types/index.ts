export type AgentEvent =
    | { type: 'thought'; content: string }
    | { type: 'tool_call'; tool: string; input: string }
    | { type: 'tool_result'; tool: string; result: string }
    | { type: 'final'; content: string }
    | { type: 'error'; content: string }

export type StepEvent = Extract<AgentEvent, { type: 'thought' | 'tool_call' | 'tool_result' }>
export type FinalEvent = Extract<AgentEvent, { type: 'final' }>
export type ErrorEvent = Extract<AgentEvent, { type: 'error' }>