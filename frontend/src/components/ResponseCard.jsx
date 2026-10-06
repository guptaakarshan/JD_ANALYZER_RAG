import React, { useEffect, useRef, useState } from 'react';
import { ChevronDown, FileText, MessageCircle } from 'lucide-react';
import SkeletonLoader from './SkeletonLoader';

export default function ResponseCard({ isLoading, qaLog, hasAnalyzed }) {
  const bottomRef = useRef(null);
  const [openEvidence, setOpenEvidence] = useState(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [qaLog, isLoading]);

  return (
    <section className="insight-section">
      <div className="section-heading"><div><p className="eyebrow">AI insight</p><h2>{qaLog.length ? 'Your answers' : 'Ask AI anything about your match.'}</h2></div><MessageCircle size={19} /></div>
      {!qaLog.length && !isLoading && <div className="compact-empty">{hasAnalyzed ? 'Ask a question above to get personalized insights about your match.' : 'Your results and answers will appear here.'}</div>}
      {isLoading && !qaLog.length && <SkeletonLoader />}
      {qaLog.length > 0 && <div className="answer-list">
        {qaLog.map((entry, index) => {
          const isOpen = openEvidence === index;
          return (
            <article className="answer-entry" key={`${entry.question}-${index}`}>
              <p className="asked-label">You asked</p>
              <p className="asked-question">“{entry.question}”</p>
              <div className="answer-copy">{entry.answer}</div>
              {entry.sources?.length > 0 && <div className="evidence-block">
                <button className="evidence-toggle" onClick={() => setOpenEvidence(isOpen ? null : index)}><span><FileText size={14} /> View evidence</span><ChevronDown size={15} className={isOpen ? 'rotate-180' : ''} /></button>
                {isOpen && <div className="evidence-list">{entry.sources.map((source) => <div className="evidence-item" key={source.id}><strong>{source.type === 'resume' ? 'Evidence from your resume' : 'Evidence from the job description'}</strong><span>{source.reference}</span><p>“{source.snippet}”</p></div>)}</div>}
              </div>}
            </article>
          );
        })}
        {isLoading && <SkeletonLoader />}
        <div ref={bottomRef} />
      </div>}
    </section>
  );
}
