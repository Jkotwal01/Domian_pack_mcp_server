/**
 * Reusable Card Component
 */
import React from 'react';
import clsx from 'clsx';

const Card = ({
  children,
  title,
  subtitle,
  actions,
  hover = false,
  className = '',
  ...props
}) => {
  return (
    <div
      className={clsx(
        'card bg-white rounded-lg shadow-card border border-gray-200 p-6',
        hover && 'card-hover transition-shadow duration-200 hover:shadow-hover',
        className
      )}
      {...props}
    >
      {(title || subtitle || actions) && (
        <div className="flex items-start justify-between mb-4">
          <div>
            {title && <h3 className="text-lg font-semibold text-gray-900">{title}</h3>}
            {subtitle && <p className="text-sm text-gray-600 mt-1">{subtitle}</p>}
          </div>
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </div>
      )}
      {children}
    </div>
  );
};

export default Card;
