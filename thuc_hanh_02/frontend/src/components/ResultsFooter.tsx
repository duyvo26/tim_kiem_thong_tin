import React from 'react';

interface ResultsFooterProps {
  onReindex: () => void;
  reindexing: boolean;
}

export const ResultsFooter: React.FC<ResultsFooterProps> = ({ onReindex, reindexing }) => {
  return (
    <footer className="bg-[#f2f2f2] text-sm text-[#70757a] mt-auto">
      <div className="max-w-[1200px] md:ml-[160px] px-4 md:px-8 py-4">
        <div className="flex flex-wrap gap-x-8 gap-y-2 items-center">
          <button 
            onClick={onReindex} 
            disabled={reindexing}
            className={`hover:underline cursor-pointer font-medium transition-colors ${reindexing ? 'animate-pulse text-blue-600' : 'text-[#1a73e8]'}`}
          >
            {reindexing ? 'Đang lập lại chỉ mục...' : 'Hệ thống: Lập lại chỉ mục toàn bộ tài liệu'}
          </button>
          <div className="md:ml-auto flex items-center gap-4">
             <span className="font-medium text-[#202124]">Võ Khương Duy - 2513464</span>
             <span className="hidden md:inline text-gray-400 italic text-xs">
              Mô hình Không gian Vector (VSM)
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};
