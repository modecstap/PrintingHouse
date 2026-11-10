import { useState } from "react";
import { requestJson } from "../../lib/api";
import { useAuthSession } from "../../lib/auth-session";
import FlexForm from "../generic/flex-form/flex-form";
import Button from "../generic/button/button";

import pageStyles from "../generic/page/page.module.css";
import styles from "./auth.module.css";

const fields = [
  {
    label: "Логин",
    path: "username",
    type: "text",
  },
  {
    label: "Пароль",
    path: "password",
    type: "password",
  },
];

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
        <FlexForm
          fields={fields}
          formData={formData}
          setFormData={setFormData}
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
