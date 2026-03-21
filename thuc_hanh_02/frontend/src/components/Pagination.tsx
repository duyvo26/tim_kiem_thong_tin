import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export const Pagination: React.FC<PaginationProps> = ({ currentPage, totalPages, onPageChange }) => {
  if (totalPages <= 1) return null;

  return (
    <div className="mt-12 flex items-center gap-4 text-sm text-[#1a73e8]">
      <button 
        onClick={() => onPageChange(Math.max(1, currentPage - 1))}
        disabled={currentPage === 1}
        className={`flex items-center gap-1 hover:underline ${currentPage === 1 ? 'invisible' : ''}`}
      >
        <ChevronLeft size={16} /> Previous
      </button>
      
      <div className="flex items-center gap-2">
        {Array.from({ length: Math.min(10, totalPages) }).map((_, i) => {
          const pageNum = i + 1;
          return (
            <button
              key={pageNum}
              onClick={() => onPageChange(pageNum)}
              className={`w-8 h-8 rounded-full flex items-center justify-center transition-colors ${
                currentPage === pageNum ? 'text-black font-bold cursor-default' : 'hover:bg-gray-100'
              }`}
            >
              {pageNum}
            </button>
          )
        })}
      </div>

      <button 
        onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
        disabled={currentPage === totalPages}
        className={`flex items-center gap-1 hover:underline ${currentPage === totalPages ? 'invisible' : ''}`}
      >
        Next <ChevronRight size={16} />
      </button>
    </div>
  );
};
