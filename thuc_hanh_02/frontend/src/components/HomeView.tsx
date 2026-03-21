import React from 'react';
import { motion } from 'motion/react';
import { Logo } from './Logo';
import { SearchBar } from './SearchBar';
import { HomeFooter } from './HomeFooter';

interface HomeViewProps {
  query: string;
  setQuery: (val: string) => void;
  handleSearch: (e?: React.FormEvent) => void;
  onReindex: () => void;
  reindexing: boolean;
}

export const HomeView: React.FC<HomeViewProps> = ({ 
  query, 
  setQuery, 
  handleSearch, 
  onReindex, 
  reindexing 
}) => {
  return (
    <div className="min-h-screen flex flex-col bg-white text-[#202124] font-sans">
      <header className="h-16" />

      <main className="flex-grow flex flex-col items-center pt-[15vh]">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col items-center w-full max-w-[584px] px-4"
        >
          <Logo className="mb-8" />
          <SearchBar 
            query={query} 
            onChange={setQuery} 
            onSearch={handleSearch} 
            onClear={() => setQuery('')}
            variant="large"
          />
        </motion.div>
      </main>

      <HomeFooter onReindex={onReindex} reindexing={reindexing} />
    </div>
  );
};
