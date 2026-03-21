import React from 'react';

export const HomeFooter: React.FC = () => {
  return (
    <footer className="bg-[#f2f2f2] text-sm text-[#70757a]">
      <div className="px-8 py-3 border-b border-[#dadce0]">Vietnam</div>
      <div className="px-8 py-3 flex flex-wrap justify-between">
        <div className="flex gap-6">
          <a href="#" className="hover:underline">About</a>
          <a href="#" className="hover:underline">Advertising</a>
          <a href="#" className="hover:underline">Business</a>
          <a href="#" className="hover:underline">How Search works</a>
        </div>
        <div className="flex gap-6">
          <a href="#" className="hover:underline">Privacy</a>
          <a href="#" className="hover:underline">Terms</a>
          <a href="#" className="hover:underline">Settings</a>
        </div>
      </div>
    </footer>
  );
};
