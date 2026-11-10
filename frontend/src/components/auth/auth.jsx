import { useState } from "react";
import { requestJson } from "../../lib/api";
import { useAuthSession } from "../../lib/auth-session";
import Button from "../generic/button/button";
import { TextField } from "../generic/text-field/text-field";

import pageStyles from "../generic/page/page.module.css";
import styles from "./auth.module.css";

const Auth = () => {
  const { login, logout: sessionLogout } = useAuthSession();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const res = await requestJson("/auth/token", {
        method: "POST",
        body: {
          username: formData.username,
          password: formData.password,
        },
      });

      if (res?.access_token) {
        login(res.access_token);
        setSuccessMsg("Вход выполнен: токен сохранён");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Произошла неизвестная ошибка");
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    sessionLogout();
    setError(null);
    setSuccessMsg("Выход выполнен");
  };

  return (
    <div className={pageStyles.page}>
      <h2>Вход</h2>

      <form onSubmit={onSubmit}>
        <TextField
          id="auth-username"
          label="Логин"
          type="text"
          value={formData.username}
          onChange={(username) => setFormData((prev) => ({ ...prev, username }))}
          disabled={loading}
        />
        <TextField
          id="auth-password"
          label="Пароль"
          type="password"
          value={formData.password}
          onChange={(password) => setFormData((prev) => ({ ...prev, password }))}
          disabled={loading}
        />

        <div className={styles.buttonRow}>
          <Button type="submit" disabled={loading}>
            Войти
          </Button>

          <Button type="button" onClick={logout}>
            Выйти
          </Button>
        </div>

        {error && <div className={styles.error}>{error}</div>}
        {successMsg && <div className={styles.success}>{successMsg}</div>}
      </form>
    </div>
  );
};

export default Auth;
