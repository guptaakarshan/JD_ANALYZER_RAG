import React, { useEffect, useRef, useState } from 'react';
import { ChevronDown, FileText, MessageCircle } from 'lucide-react';
import SkeletonLoader from './SkeletonLoader';

function cleanAnswerText(text) {
  if (!text) return '';
  return text
    .replace(/\[(?:resume|jd)-\d+\]/gi, '')
    .replace(/\s{2,}/g, ' ')
    .replace(/\s+([.,;:!?])/g, '$1')
    .trim();
}

export default function ResponseCard({ isLoading, qaLog, hasAnalyzed }) {
  const bottomRef = useRef(null);
  const [closedEvidence, setClosedEvidence] = useState({});

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
          const isClosed = Boolean(closedEvidence[index]);
          return (
            <article className="answer-entry" key={`${entry.question}-${index}`}>
              <p className="asked-label">You asked</p>
              <p className="asked-question">“{entry.question}”</p>
              <div className="answer-copy">{cleanAnswerText(entry.answer)}</div>
              {entry.sources?.length > 0 && <div className="evidence-block">
                <button
                  className="evidence-toggle"
                  onClick={() => setClosedEvidence((prev) => ({ ...prev, [index]: !prev[index] }))}
                  aria-label="Toggle evidence details"
                >
                  <span><FileText size={14} /> Evidence ({entry.sources.length})</span>
                  <ChevronDown size={15} className={isClosed ? '' : 'rotate-180'} />
                </button>
                {!isClosed && (
                  <div className="evidence-list">
                    {entry.sources.map((source, sIdx) => {
                      const typeLabel = source.document_type === 'resume' ? 'Resume' : 'Job Description';
                      const pageLabel = source.page ? ` · Page ${source.page}` : '';
                      return (
                        <div className="evidence-item" key={source.label || sIdx}>
                          <strong>Evidence</strong>
                          <span>{typeLabel}{pageLabel}</span>
                          <p>“{source.snippet}”</p>
                        </div>
                      );
                    })}
                  </div>
                )}
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
