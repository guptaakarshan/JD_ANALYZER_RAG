import React, { useState } from 'react';
import { ArrowRight, HelpCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const SUGGESTIONS = [
  'What skills am I missing?',
  'Why is my match score low?',
  'Does my experience fit this role?',
  'How can I improve my resume?',
  'What are my strongest qualifications?',
];

export default function AskAISection({ onAsk, isLoading, disabled }) {
  const [question, setQuestion] = useState('');

  const submit = (value) => {
    if (!value.trim()) {
      toast.error('Write a question first.');
      return;
    }
    onAsk(value.trim());
    setQuestion('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    submit(question);
  };

  return (
    <section className="ask-section compact-ask animate-fade-up">
      <div className="ask-header">
        <div className="ask-icon-wrap">
          <HelpCircle size={18} />
        </div>
        <div>
          <p className="ask-title">HAVE QUESTIONS ABOUT YOUR MATCH?</p>
          <p className="ask-subtitle">Ask anything about your resume or this role.</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="ask-form-wrap">
        <div className="ask-input-row">
          <input
            className="ask-input"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={disabled || isLoading}
            placeholder="Ask something about your match..."
            aria-label="Ask something about your match"
          />
          <button type="submit" className="ask-submit" disabled={disabled || isLoading}>
            {isLoading ? (
              <span className="spinner" />
            ) : (
              <>Ask <ArrowRight size={14} /></>
            )}
          </button>
        </div>
      </form>

      <div className="suggestions-wrap">
        <span className="suggestion-label">Suggested:</span>
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            type="button"
            className="suggestion-chip"
            onClick={() => submit(s)}
            disabled={disabled || isLoading}
          >
            {s}
          </button>
        ))}
      </div>
    </section>
  );
}
