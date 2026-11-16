import type { AgentEvent } from '../types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:3002/api'

export async function streamRun(
    task: string,
    onEvent: (event: AgentEvent) => void,
    signal?: AbortSignal
): Promise<void> {
    const response = await fetch(`${API_URL}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task }),
        signal,
    })

    if (!response.ok || !response.body) {
        throw new Error(`Request failed with status ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        // Messages are separated by a blank line. The last piece may be incomplete.
        const messages = buffer.split('\n\n')
        buffer = messages.pop() ?? ''

        for (const message of messages) {
            if (!message.startsWith('data: ')) continue
            onEvent(JSON.parse(message.slice(6)) as AgentEvent)
        }
    }
}