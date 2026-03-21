import React from 'react';

interface SearchTabsProps {
  activeTab: "keyword" | "phrase";
  onTabChange: (tab: "keyword" | "phrase") => void;
  className?: string;
}

export const SearchTabs: React.FC<SearchTabsProps> = ({ activeTab, onTabChange, className = "" }) => {
  return (
    <div className={`flex items-center gap-6 border-b border-gray-200 ${className}`}>
      <button
        type="button"
        onClick={() => onTabChange("keyword")}
        className={`pb-3 px-1 text-sm font-medium transition-colors relative ${
          activeTab === "keyword" 
            ? "text-[#1a73e8]" 
            : "text-gray-600 hover:text-gray-900"
        }`}
      >
        Từ khóa (Keyword)
        {activeTab === "keyword" && (
          <div className="absolute bottom-0 left-0 right-0 h-[3px] bg-[#1a73e8] rounded-t-full" />
        )}
      </button>
      
      <button
        type="button"
        onClick={() => onTabChange("phrase")}
        className={`pb-3 px-1 text-sm font-medium transition-colors relative ${
          activeTab === "phrase" 
            ? "text-[#1a73e8]" 
            : "text-gray-600 hover:text-gray-900"
        }`}
      >
        Mệnh đề (Phrase)
        {activeTab === "phrase" && (
          <div className="absolute bottom-0 left-0 right-0 h-[3px] bg-[#1a73e8] rounded-t-full" />
        )}
      </button>
    </div>
  );
};
