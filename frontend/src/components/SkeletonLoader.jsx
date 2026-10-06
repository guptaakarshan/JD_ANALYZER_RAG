import React from 'react';

export default function SkeletonLoader() {
  return (
    <div className="skeleton-wrap">
      <div className="skeleton-line" style={{ width: '30%', height: 10, marginBottom: 12 }} />
      <div className="skeleton-line" style={{ width: '100%' }} />
      <div className="skeleton-line" style={{ width: '88%' }} />
      <div className="skeleton-line" style={{ width: '72%', marginBottom: 0 }} />
    </div>
  );
}
