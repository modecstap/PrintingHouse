import { useState } from "react";
import styles from "./tabs.module.css";

export function Tabs({ tabs, defaultSelectedId, isTabDisabled }) {
  const [selected, setSelected] = useState(
    defaultSelectedId ?? tabs[0].id,
  );
  const [menuOpen, setMenuOpen] = useState(false);

  const selectTab = (id) => {
    if (isTabDisabled?.(id)) {
      return;
    }
    setSelected(id);
    setMenuOpen(false);
  };

  return (
    <div className={styles.layout}>
      <nav
        className={`${styles.menu} ${menuOpen ? styles.menuOpen : ""}`}
        role="tablist"
        aria-orientation="vertical"
      >
        <button
          className={styles.burger}
          type="button"
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen(!menuOpen)}
        >
          ☰
        </button>
        {tabs.map(({ id, label }) => {
          const disabled = isTabDisabled?.(id) ?? false;
          return (
            <button
              key={id}
              className={styles.tab}
              type="button"
              role="tab"
              aria-selected={id === selected}
              disabled={disabled}
              title={
                disabled ? "Войдите, чтобы открыть этот раздел" : undefined
              }
              onClick={() => selectTab(id)}
            >
              {label}
            </button>
          );
        })}
      </nav>
      <div className={styles.content}>
        {tabs.map(({ id, Content }) => (
          <div
            key={id}
            role="tabpanel"
            hidden={id !== selected}
            className={styles.panel}
          >
            <Content />
          </div>
        ))}
      </div>
    </div>
  );
}
