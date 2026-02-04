/**
 * Spinner/Loading Component
 */
import React from 'react';
import clsx from 'clsx';

const Spinner = ({ size = 'md', className = '' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-6 h-6 border-2',
    lg: 'w-8 h-8 border-3',
    xl: 'w-12 h-12 border-4',
  };

  return (
    <div
      className={clsx(
        'spinner inline-block border-primary border-t-transparent rounded-full animate-spin',
        sizeClasses[size],
        className
      )}
    />
  );
};

export default Spinner;
