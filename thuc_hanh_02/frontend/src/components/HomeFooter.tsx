import React from 'react';

interface HomeFooterProps {
  onReindex: () => void;
  reindexing: boolean;
}

export const HomeFooter: React.FC<HomeFooterProps> = ({ onReindex, reindexing }) => {
  return (
    <footer className="bg-[#f2f2f2] text-sm text-[#70757a]">
      <div className="px-8 py-3 border-b border-[#dadce0]">Việt Nam</div>
      <div className="px-8 py-3 flex flex-wrap justify-between items-center">
        <div className="flex gap-6">
          <button 
            onClick={onReindex} 
            disabled={reindexing}
            className={`hover:underline cursor-pointer font-medium transition-colors ${reindexing ? 'text-blue-600 animate-pulse' : 'text-[#1a73e8]'}`}
          >
            {reindexing ? 'Đang cập nhật chỉ mục...' : 'Hệ thống: Lập lại chỉ mục dữ liệu'}
          </button>
        </div>
        <div className="flex gap-4 items-center">
          <span className="font-medium text-[#202124]">Võ Khương Duy - 2513464</span>
          <span className="text-gray-300">|</span>
          <span className="italic text-xs">GooSearch Core Engine</span>
        </div>
      </div>
    </footer>
  );
};
