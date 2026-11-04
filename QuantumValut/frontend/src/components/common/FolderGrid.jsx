import React from 'react';

const FolderGrid = ({ children }) => {
  return (
    <div className="files-container" id="files-container">
      {children}
    </div>
  );
};

export default FolderGrid;
