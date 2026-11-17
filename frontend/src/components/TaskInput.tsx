import { useState } from 'react'
import type { KeyboardEvent } from 'react'

interface TaskInputProps {
    isRunning: boolean
    onSubmit: (task: string) => void
    onStop: () => void
}

export default function TaskInput({ isRunning, onSubmit, onStop }: TaskInputProps) {
    const [value, setValue] = useState('')

    const submit = () => {
        const task = value.trim()
        if (!task || isRunning) return
        onSubmit(task)
        setValue('')
    }

    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        // Enter sends, Shift+Enter inserts a new line
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            submit()
        }
    }

    return (
        <div className="flex gap-3 items-end">
      <textarea
          value={value}
          onChange={e => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={2}
          maxLength={2000}
          placeholder="Give the agent a task..."
          className="flex-1 resize-none rounded-xl bg-gray-900 border border-gray-700
          text-gray-100 text-sm px-4 py-3 placeholder:text-gray-500
          focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
            {isRunning ? (
                <button
                    onClick={onStop}
                    className="rounded-xl bg-red-600 hover:bg-red-700 text-white text-sm font-medium px-5 py-3"
                >
                    Stop
                </button>
            ) : (
                <button
                    onClick={submit}
                    disabled={!value.trim()}
                    className="rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium
            px-5 py-3 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    Send
                </button>
            )}
        </div>
    )
}