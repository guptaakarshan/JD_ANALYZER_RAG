import React, { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

export default function AskAISection({ onAsk, isLoading }) {
  const [question, setQuestion] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!question.trim()) {
      toast.error('Please type a question.');
      return;
    }
    onAsk(question.trim());
    setQuestion('');
  };

  return (
    <section className="bg-white rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all duration-300 p-6">
      <p className="text-xs font-semibold uppercase tracking-widest text-gray-400 mb-4">
        3. Ask a Question
      </p>

      <form onSubmit={handleSubmit} className="flex gap-3">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={isLoading}
          placeholder="Ask anything about the resume and job description..."
          className="flex-1 rounded-xl border border-gray-200 bg-gray-50/20 focus:bg-white px-4 py-3 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
        />
        <button
          type="submit"
          disabled={isLoading}
          className="bg-black hover:bg-zinc-800 disabled:opacity-70 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg text-sm font-semibold flex items-center gap-2 transition-all duration-200 active:scale-[0.98] shrink-0 min-w-[110px] justify-center shadow-sm hover:shadow-md cursor-pointer"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin text-white" />
              <span>Asking…</span>
            </>
          ) : (
            <>
              <Send className="h-4 w-4" />
              <span>Ask AI</span>
            </>
          )}
        </button>
      </form>
    </section>
  );
}
