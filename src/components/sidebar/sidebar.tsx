import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faHome, 
  faPaintbrush,
  faCalculator,
  faLaptopCode,
  faBook,
  faCog,
  faSun,
  faMoon,
  faEllipsisV,
  faExternalLinkAlt,
  faStar,
  faHistory,
  faBookmark,
  IconDefinition
} from '@fortawesome/free-solid-svg-icons';
import './sidebar.css';

interface MenuItem {
  id: string | number;
  icon: IconDefinition;
  label: string;
  path?: string;
  dropdown?: {
    id: string;
    label: string;
  }[];
}

interface SubmenuItem {
  icon: IconDefinition;
  label: string;
}

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [theme, setTheme] = useState('dark');
  const [activeDropdown, setActiveDropdown] = useState<string | number | null>(null);
  const [activeSubmenu, setActiveSubmenu] = useState<string | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const submenuTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  const handleMouseEnter = (id: string | number) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setActiveDropdown(id);
  };

  const handleMouseLeave = () => {
    timeoutRef.current = setTimeout(() => {
      setActiveDropdown(null);
    }, 300);
  };

  const handleSubmenuEnter = (id: string) => {
    if (submenuTimeoutRef.current) {
      clearTimeout(submenuTimeoutRef.current);
    }
    setActiveSubmenu(id);
  };

  const handleSubmenuLeave = () => {
    submenuTimeoutRef.current = setTimeout(() => {
      setActiveSubmenu(null);
    }, 300);
  };

  const topMenuItems: MenuItem[] = [
    { id: 'home', icon: faHome, label: 'Главная', path: '/' },
    { id: 'draw', icon: faPaintbrush, label: 'Рисовалка', path: '/drawpad' },
  ];

  const subjectMenuItems: MenuItem[] = [
    { 
      id: 3, 
      icon: faCalculator, 
      label: 'Математика',
      dropdown: [
        { id: 'math1', label: 'Алгебра' },
        { id: 'math2', label: 'Геометрия' },
        { id: 'math3', label: 'Тригонометрия' }
      ]
    },
    { 
      id: 4, 
      icon: faLaptopCode, 
      label: 'Информатика',
      dropdown: [
        { id: 'info1', label: 'Программирование' },
        { id: 'info2', label: 'Алгоритмы' },
        { id: 'info3', label: 'Базы данных' }
      ]
    },
    { 
      id: 5, 
      icon: faBook, 
      label: 'Русский язык',
      dropdown: [
        { id: 'rus1', label: 'Грамматика' },
        { id: 'rus2', label: 'Орфография' },
        { id: 'rus3', label: 'Пунктуация' }
      ]
    },
  ];

  const bottomMenuItems: MenuItem[] = [
    { id: 'settings', icon: faCog, label: 'Настройки', path: "/settings" },
  ];

  const submenuItems: SubmenuItem[] = [
    { icon: faExternalLinkAlt, label: 'Открыть в новом окне' },
    { icon: faStar, label: 'Добавить в избранное' },
  ];

  const renderSimpleMenuItem = (item: MenuItem) => (
    <li 
      key={item.id} 
      className={`menu-item ${location.pathname === item.path ? 'active' : ''} ${item.id === 'settings' ? 'settings-button' : ''}`}
      data-tooltip={item.label}
      onClick={() => item.path && navigate(item.path)}
    >
      <FontAwesomeIcon icon={item.icon} />
    </li>
  );

  const renderDropdownMenuItem = (item: MenuItem) => (
    <li 
      key={item.id} 
      className="menu-item"
      data-tooltip={item.label}
      data-has-dropdown="true"
      onMouseEnter={() => handleMouseEnter(item.id)}
      onMouseLeave={handleMouseLeave}
    >
      <FontAwesomeIcon icon={item.icon} />
      <div className={`dropdown-menu ${activeDropdown === item.id ? 'show' : ''}`}>
        {item.dropdown?.map((subItem) => (
          <div key={subItem.id} className="dropdown-item">
            <span>{subItem.label}</span>
            <div 
              className="submenu-trigger"
              onMouseEnter={() => handleSubmenuEnter(subItem.id)}
              onMouseLeave={handleSubmenuLeave}
            >
              <FontAwesomeIcon icon={faEllipsisV} />
              <div className={`submenu ${activeSubmenu === subItem.id ? 'show' : ''}`}>
                {submenuItems.map((submenuItem, index) => (
                  <div key={index} className="submenu-item">
                    <FontAwesomeIcon icon={submenuItem.icon} />
                    <span>{submenuItem.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </li>
  );

  return (
    <div className="sidebar">
      <div className="sidebar-top">
        <ul className="sidebar-menu">
          {topMenuItems.map(renderSimpleMenuItem)}
        </ul>
      </div>

      <div className="sidebar-middle">
        <ul className="sidebar-menu">
          {subjectMenuItems.map(renderDropdownMenuItem)}
        </ul>
      </div>

      <div className="sidebar-bottom">
        <ul className="sidebar-menu">
          {bottomMenuItems.map(renderSimpleMenuItem)}
        </ul>
        <div className="theme-toggle" onClick={toggleTheme} title="Сменить тему">
          <FontAwesomeIcon icon={theme === 'dark' ? faSun : faMoon} />
        </div>
      </div>
    </div>
  );
};

export default Sidebar; 