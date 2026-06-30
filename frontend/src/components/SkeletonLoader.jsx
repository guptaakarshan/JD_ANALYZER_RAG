import React from 'react';

export default function SkeletonLoader() {
  return (
    <div className="flex justify-start w-full animate-pulse">
      <div className="bg-gray-50 border border-gray-100 rounded-2xl rounded-tl-sm p-4 w-[85%] space-y-3">
        <div className="h-3 bg-gray-200 rounded w-1/4"></div>
        <div className="space-y-2">
          <div className="h-4 bg-gray-200 rounded w-full"></div>
          <div className="h-4 bg-gray-200 rounded w-[92%]"></div>
          <div className="h-4 bg-gray-200 rounded w-[78%]"></div>
        </div>
      </div>
    </div>
  );
}
