import { useState } from 'react';

interface MenuProps {
  items: string[];
  selectedItem: string | null;
  onSelectItem: (item: string) => void;
  title: string;
  color?: string;
}

const Menu = ({ items, selectedItem, onSelectItem, title, color = '#8B0000' }: MenuProps) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredItems = items.filter(item =>
    item.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div style={{
      width: '280px',
      height: '100vh',
      backgroundColor: '#1a1a1a',
      borderRight: '2px solid #333',
      display: 'flex',
      flexDirection: 'column',
      position: 'fixed',
      left: 0,
      top: 0,
      overflowY: 'auto'
    }}>
      {/* Header */}
      <div style={{
        padding: '20px',
        backgroundColor: color,
        color: 'white',
        fontWeight: 'bold',
        fontSize: '1.2rem',
        borderBottom: '2px solid rgba(255,255,255,0.1)'
      }}>
        {title}
      </div>

      {/* Search Box */}
      <div style={{ padding: '15px' }}>
        <input
          type="text"
          placeholder="Search..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            width: '100%',
            padding: '10px',
            border: '1px solid #444',
            borderRadius: '5px',
            backgroundColor: '#2a2a2a',
            color: '#fff',
            fontSize: '0.9rem',
            outline: 'none'
          }}
        />
      </div>

      {/* Items List */}
      <div style={{ flex: 1, overflowY: 'auto' }}>
        {filteredItems.length === 0 ? (
          <div style={{ padding: '20px', color: '#888', textAlign: 'center' }}>
            No items found
          </div>
        ) : (
          filteredItems.map(item => (
            <div
              key={item}
              onClick={() => onSelectItem(item)}
              style={{
                padding: '15px 20px',
                cursor: 'pointer',
                backgroundColor: selectedItem === item ? color : 'transparent',
                color: selectedItem === item ? 'white' : '#ccc',
                borderLeft: selectedItem === item ? `4px solid ${color}` : '4px solid transparent',
                transition: 'all 0.2s ease',
                fontSize: '0.95rem',
                borderBottom: '1px solid #2a2a2a'
              }}
              onMouseEnter={(e) => {
                if (selectedItem !== item) {
                  e.currentTarget.style.backgroundColor = '#2a2a2a';
                }
              }}
              onMouseLeave={(e) => {
                if (selectedItem !== item) {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }
              }}
            >
              {item}
            </div>
          ))
        )}
      </div>

      {/* Footer Info */}
      <div style={{
        padding: '15px',
        borderTop: '1px solid #333',
        color: '#888',
        fontSize: '0.85rem',
        textAlign: 'center'
      }}>
        {filteredItems.length} item{filteredItems.length !== 1 ? 's' : ''}
      </div>
    </div>
  );
};

export default Menu;
