import { useCallback, useRef, useState } from 'react'
import { streamRun } from '../api/agent'
import type { AgentEvent } from '../types'

export interface Turn {
    id: string
    task: string
    events: AgentEvent[]
    status: 'running' | 'done' | 'error' | 'stopped'
}

export function useAgent() {
    const [turns, setTurns] = useState<Turn[]>([])
    const abortRef = useRef<AbortController | null>(null)

    const isRunning = turns[turns.length - 1]?.status === 'running'

    const run = useCallback(async (task: string) => {
        const id = crypto.randomUUID()
        const controller = new AbortController()
        abortRef.current = controller

        setTurns(prev => [...prev, { id, task, events: [], status: 'running' }])

        const update = (fn: (turn: Turn) => Turn) =>
            setTurns(prev => prev.map(t => (t.id === id ? fn(t) : t)))

        try {
            await streamRun(
                task,
                (event: AgentEvent) => {
                    update(t => ({
                        ...t,
                        events: [...t.events, event],
                        status:
                            event.type === 'error' ? 'error'
                                : event.type === 'final' ? 'done'
                                    : 'running',
                    }))
                },
                controller.signal
            )
            // Stream ended without a final or error event
            update(t => (t.status === 'running' ? { ...t, status: 'done' } : t))
        } catch (err) {
            if (controller.signal.aborted) {
                update(t => ({ ...t, status: 'stopped' }))
            } else {
                const message = err instanceof Error ? err.message : 'Something went wrong'
                update(t => ({
                    ...t,
                    status: 'error',
                    events: [...t.events, { type: 'error', content: message }],
                }))
            }
        }
    }, [])

    const stop = useCallback(() => abortRef.current?.abort(), [])

    return { turns, isRunning, run, stop }
}