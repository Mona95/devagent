import type { Turn } from '../hooks/useAgent'
import type { ErrorEvent, FinalEvent, StepEvent } from '../types'
import EventStep from './EventStep'

const isStep = (e: Turn['events'][number]): e is StepEvent =>
    e.type === 'thought' || e.type === 'tool_call' || e.type === 'tool_result'
const isFinal = (e: Turn['events'][number]): e is FinalEvent => e.type === 'final'
const isError = (e: Turn['events'][number]): e is ErrorEvent => e.type === 'error'

export default function TurnView({ turn }: { turn: Turn }) {
    const steps = turn.events.filter(isStep)
    const final = turn.events.find(isFinal)
    const error = turn.events.find(isError)

    return (
        <div className="flex flex-col gap-3">
            {/* User's task */}
            <div className="self-end max-w-[80%] rounded-2xl bg-blue-600 text-white text-sm px-4 py-2.5">
                {turn.task}
            </div>

            {/* Agent steps */}
            {steps.length > 0 && (
                <div className="flex flex-col gap-2">
                    {steps.map((event, i) => (
                        <EventStep key={i} event={event} />
                    ))}
                </div>
            )}

            {turn.status === 'running' && (
                <p className="text-sm text-gray-500 animate-pulse px-3">Agent is working...</p>
            )}

            {turn.status === 'stopped' && (
                <p className="text-sm text-amber-400 px-3">Stopped.</p>
            )}

            {/* Final answer */}
            {final && (
                <div className="rounded-2xl border border-gray-800 bg-gray-900 text-gray-100 text-sm px-4 py-3 whitespace-pre-wrap">
                    {final.content}
                </div>
            )}

            {error && (
                <div className="rounded-lg border border-red-800 bg-red-950 text-red-300 text-sm px-4 py-3">
                    {error.content}
                </div>
            )}
        </div>
    )
}