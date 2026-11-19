import { useEffect, useRef } from 'react'
import { useAgent } from './hooks/useAgent'
import TurnView from './components/TurnView'
import TaskInput from './components/TaskInput'

const EXAMPLE_TASKS = [
    'Look at the GitHub repo tiangolo/fastapi and summarize what it does',
    'Search the web for the latest stable Python version',
    'Read https://fastapi.tiangolo.com and list its main features',
]

export default function App() {
    const { turns, isRunning, run, stop } = useAgent()
    const bottomRef = useRef<HTMLDivElement>(null)

    // Keep the newest event in view as the agent streams
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [turns])

    return (
        <div className="h-screen bg-gray-950 text-gray-100 flex flex-col">
            {/* Header */}
            <header className="border-b border-gray-800 px-6 py-4">
                <h1 className="text-lg font-bold">
                    Dev<span className="text-blue-500">Agent</span>
                </h1>
                <p className="text-xs text-gray-500">
                    Autonomous agent with web search, code execution and GitHub tools
                </p>
            </header>

            {/* Conversation */}
            <main className="flex-1 overflow-y-auto">
                <div className="max-w-3xl mx-auto px-6 py-6 flex flex-col gap-8">
                    {turns.length === 0 && (
                        <div className="text-center py-16">
                            <p className="text-gray-400 mb-6">
                                Give the agent a task and watch it decide which tools to use.
                            </p>
                            <div className="flex flex-col gap-2 items-center">
                                {EXAMPLE_TASKS.map(task => (
                                    <button
                                        key={task}
                                        onClick={() => run(task)}
                                        disabled={isRunning}
                                        className="text-sm text-gray-300 border border-gray-800 hover:border-gray-600
                      rounded-lg px-4 py-2 transition-colors disabled:opacity-50"
                                    >
                                        {task}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {turns.map(turn => (
                        <TurnView key={turn.id} turn={turn} />
                    ))}

                    <div ref={bottomRef} />
                </div>
            </main>

            {/* Input */}
            <footer className="border-t border-gray-800 px-6 py-4">
                <div className="max-w-3xl mx-auto">
                    <TaskInput isRunning={isRunning} onSubmit={run} onStop={stop} />
                </div>
            </footer>
        </div>
    )
}