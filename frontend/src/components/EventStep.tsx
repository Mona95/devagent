import type { StepEvent } from '../types'

function formatInput(raw: string): string {
    try {
        return JSON.stringify(JSON.parse(raw), null, 2)
    } catch {
        return raw
    }
}

export default function EventStep({ event }: { event: StepEvent }) {
    if (event.type === 'thought') {
        return (
            <div className="text-sm text-gray-400 italic px-3 py-2">
                🧠 {event.content}
            </div>
        )
    }

    if (event.type === 'tool_call') {
        return (
            <div className="rounded-lg border border-blue-900 bg-blue-950/40 px-3 py-2">
                <p className="text-xs font-medium text-blue-300 mb-1">
                    🔧 Using tool: {event.tool}
                </p>
                <pre className="text-xs text-gray-300 whitespace-pre-wrap break-words font-mono">
          {formatInput(event.input)}
        </pre>
            </div>
        )
    }

    return (
        <div className="rounded-lg border border-gray-800 bg-gray-900 px-3 py-2">
            <p className="text-xs font-medium text-gray-500 mb-1">
                📄 Result from {event.tool}
            </p>
            <pre className="text-xs text-gray-400 whitespace-pre-wrap break-words font-mono">
        {event.result}
      </pre>
        </div>
    )
}