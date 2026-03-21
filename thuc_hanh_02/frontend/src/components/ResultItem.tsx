import React from 'react';
import { Search, MoreVertical } from 'lucide-react';
import { motion } from 'motion/react';
import { SearchResult } from '../types';

interface ResultItemProps {
  result: SearchResult;
  index: number;
}

export const ResultItem: React.FC<ResultItemProps> = ({ result, index }) => {
  let hostname = '';
  try {
    hostname = new URL(result.url).hostname;
  } catch (e) {
    hostname = result.url;
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="max-w-[652px] group"
    >
      <div className="flex flex-col">
        <div className="flex items-center gap-2 text-sm mb-1">
          <div className="w-7 h-7 bg-gray-100 rounded-full flex items-center justify-center overflow-hidden">
            <Search size={14} className="text-gray-400" />
          </div>
          <div className="flex flex-col overflow-hidden">
            <span className="text-[#202124] text-sm truncate">{hostname}</span>
            <span className="text-[#70757a] text-xs truncate">{result.url}</span>
          </div>
          <button className="ml-auto p-1 text-gray-400 hover:text-gray-600">
            <MoreVertical size={16} />
          </button>
        </div>
        <a href={result.url} target="_blank" rel="noopener noreferrer" className="group">
          <h3 className="text-[#1a0dab] text-xl font-medium hover:underline mb-1">
            {result.title}
          </h3>
        </a>
        <p className="text-[#4d5156] text-sm leading-relaxed">
          {result.snippet}
        </p>
      </div>
    </motion.div>
  );
};
