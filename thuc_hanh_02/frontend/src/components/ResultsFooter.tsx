import React from 'react';

export const ResultsFooter: React.FC = () => {
  return (
    <footer className="bg-[#f2f2f2] text-sm text-[#70757a] mt-auto">
      <div className="px-4 md:px-8 py-3 border-b border-[#dadce0] md:pl-[160px]">Vietnam</div>
      <div className="px-4 md:px-8 py-3 flex flex-wrap gap-6 md:pl-[160px]">
        <a href="#" className="hover:underline">Help</a>
        <a href="#" className="hover:underline">Send feedback</a>
        <a href="#" className="hover:underline">Privacy</a>
        <a href="#" className="hover:underline">Terms</a>
      </div>
    </footer>
  );
};
