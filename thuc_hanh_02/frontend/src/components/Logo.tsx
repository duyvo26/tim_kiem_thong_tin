import React from 'react';

interface LogoProps {
  className?: string;
  size?: 'sm' | 'lg';
}

export const Logo: React.FC<LogoProps> = ({ className = '', size = 'lg' }) => {
  const sizeClasses = size === 'lg' ? 'text-7xl' : 'text-3xl';
  
  return (
    <div className={`select-none cursor-default ${className}`}>
      <span className={`${sizeClasses} font-bold tracking-tighter flex`}>
        <span className="text-[#4285F4]">G</span>
        <span className="text-[#EA4335]">o</span>
        <span className="text-[#FBBC05]">o</span>
        <span className="text-[#4285F4]">S</span>
        <span className="text-[#34A853]">e</span>
        <span className="text-[#EA4335]">a</span>
        <span className="text-[#FBBC05]">r</span>
        <span className="text-[#4285F4]">c</span>
        <span className="text-[#34A853]">h</span>
      </span>
    </div>
  );
};
