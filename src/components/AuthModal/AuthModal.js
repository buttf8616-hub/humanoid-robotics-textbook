import React, { useState } from 'react';
import { useAuth } from '@site/src/context/AuthContext';
import styles from './AuthModal.module.css';

const SW_OPTIONS = [
  { value: 'Beginner', label: 'Beginner', desc: 'New to programming or just starting out' },
  { value: 'Intermediate', label: 'Intermediate', desc: 'Comfortable with at least one language' },
  { value: 'Advanced', label: 'Advanced', desc: 'Professional / multiple languages / systems' },
];

const HW_OPTIONS = [
  { value: 'None', label: 'No Experience', desc: 'Never worked with hardware' },
  { value: 'Basic', label: 'Basic', desc: 'Tried Arduino / Raspberry Pi hobby projects' },
  { value: 'Intermediate', label: 'Intermediate', desc: 'Built circuits, sensors, actuators' },
  { value: 'Advanced', label: 'Advanced', desc: 'Robotics, embedded systems, PCB design' },
];

function RadioGroup({ options, value, onChange }) {
  return (
    <div className={styles.radioGroup}>
      {options.map((opt) => (
        <label
          key={opt.value}
          className={`${styles.radioOption} ${value === opt.value ? styles.radioSelected : ''}`}
          onClick={() => onChange(opt.value)}
        >
          <span className={styles.radioCheck} />
          <span style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <span className={styles.radioLabel}>{opt.label}</span>
            <span className={styles.radioDesc}>{opt.desc}</span>
          </span>
        </label>
      ))}
    </div>
  );
}

function SignupForm({ onSwitch, onSuccess }) {
  const { signup } = useAuth();
  const [step, setStep] = useState(1);
  const [values, setValues] = useState({
    email: '',
    name: '',
    codeId: '',
    password: '',
    softwareBg: '',
    hardwareBg: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const set = (k) => (v) =>
    setValues((prev) => ({ ...prev, [k]: typeof v === 'string' && v.target ? v.target.value : v }));

  const handleInput = (k) => (e) => setValues((prev) => ({ ...prev, [k]: e.target.value }));

  const nextStep = (e) => {
    e.preventDefault();
    setError('');
    if (!values.name.trim() || !values.email.trim() || !values.codeId.trim() || values.password.length < 6) {
      setError('Please fill in all fields. Password must be at least 6 characters.');
      return;
    }
    setStep(2);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!values.softwareBg || !values.hardwareBg) {
      setError('Please select your background level for both software and hardware.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await signup(
        values.email,
        values.name,
        values.codeId,
        values.password,
        values.softwareBg,
        values.hardwareBg
      );
      onSuccess();
    } catch (err) {
      setError(err.message);
      setStep(1);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className={styles.stepBar}>
        <div className={`${styles.step} ${step >= 1 ? styles.stepActive : ''}`}>1 Account</div>
        <div className={styles.stepLine} />
        <div className={`${styles.step} ${step >= 2 ? styles.stepActive : ''}`}>2 Background</div>
      </div>

      {step === 1 ? (
        <form className={styles.form} onSubmit={nextStep}>
          {error && <div className={styles.error}>{error}</div>}
          <div className={styles.field}>
            <label className={styles.label}>Full Name</label>
            <input
              className={styles.input}
              type="text"
              placeholder="Your full name"
              value={values.name}
              onChange={handleInput('name')}
              required
              autoFocus
            />
          </div>
          <div className={styles.field}>
            <label className={styles.label}>Email</label>
            <input
              className={styles.input}
              type="email"
              placeholder="you@example.com"
              value={values.email}
              onChange={handleInput('email')}
              required
            />
          </div>
          <div className={styles.field}>
            <label className={styles.label}>PIAIC Student Code</label>
            <input
              className={styles.input}
              type="text"
              placeholder="e.g. PIAIC12345"
              value={values.codeId}
              onChange={handleInput('codeId')}
              required
            />
            <span className={styles.codeHint}>Your PIAIC registration code</span>
          </div>
          <div className={styles.field}>
            <label className={styles.label}>Password</label>
            <input
              className={styles.input}
              type="password"
              placeholder="Minimum 6 characters"
              value={values.password}
              onChange={handleInput('password')}
              required
              minLength={6}
            />
          </div>
          <button type="submit" className={styles.submitBtn}>
            Next: Your Background →
          </button>
          <div className={styles.switchRow}>
            Already have an account?{' '}
            <button type="button" className={styles.switchBtn} onClick={onSwitch}>
              Sign in
            </button>
          </div>
        </form>
      ) : (
        <form className={styles.form} onSubmit={handleSubmit}>
          {error && <div className={styles.error}>{error}</div>}
          <div className={styles.bgSection}>
            <p className={styles.bgIntro}>
              This helps us personalise robotics content to match your level.
            </p>
            <div className={styles.field}>
              <label className={styles.label}>💻 Software / Programming Experience</label>
              <RadioGroup
                options={SW_OPTIONS}
                value={values.softwareBg}
                onChange={set('softwareBg')}
              />
            </div>
            <div className={styles.field}>
              <label className={styles.label}>🔧 Hardware / Electronics Experience</label>
              <RadioGroup
                options={HW_OPTIONS}
                value={values.hardwareBg}
                onChange={set('hardwareBg')}
              />
            </div>
          </div>
          <div className={styles.btnRow}>
            <button
              type="button"
              className={styles.backBtn}
              onClick={() => { setStep(1); setError(''); }}
            >
              ← Back
            </button>
            <button type="submit" className={styles.submitBtn} disabled={loading}>
              {loading ? 'Creating account...' : 'Create Account'}
            </button>
          </div>
        </form>
      )}
    </>
  );
}

function SigninForm({ onSwitch, onSuccess }) {
  const { signin } = useAuth();
  const [values, setValues] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const set = (k) => (e) => setValues((v) => ({ ...v, [k]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await signin(values.email, values.password);
      onSuccess();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      {error && <div className={styles.error}>{error}</div>}
      <div className={styles.field}>
        <label className={styles.label}>Email</label>
        <input
          className={styles.input}
          type="email"
          placeholder="you@example.com"
          value={values.email}
          onChange={set('email')}
          required
          autoFocus
        />
      </div>
      <div className={styles.field}>
        <label className={styles.label}>Password</label>
        <input
          className={styles.input}
          type="password"
          placeholder="Your password"
          value={values.password}
          onChange={set('password')}
          required
        />
      </div>
      <button type="submit" className={styles.submitBtn} disabled={loading}>
        {loading ? 'Signing in...' : 'Sign In'}
      </button>
      <div className={styles.switchRow}>
        No account yet?{' '}
        <button type="button" className={styles.switchBtn} onClick={onSwitch}>
          Create one
        </button>
      </div>
    </form>
  );
}

export function AuthModal({ onClose, defaultMode = 'signin' }) {
  const [mode, setMode] = useState(defaultMode);

  return (
    <div className={styles.overlay} onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className={styles.modal}>
        <button className={styles.closeBtn} onClick={onClose} aria-label="Close">
          ×
        </button>
        <div className={styles.header}>
          <span className={styles.icon}>🤖</span>
          <h2 className={styles.title}>
            {mode === 'signup' ? 'Join Robot Academy' : 'Robot Academy'}
          </h2>
          <p className={styles.subtitle}>
            {mode === 'signup'
              ? 'Create your personalised learning profile'
              : 'Sign in to access personalised features'}
          </p>
        </div>
        {mode === 'signin' ? (
          <SigninForm onSwitch={() => setMode('signup')} onSuccess={onClose} />
        ) : (
          <SignupForm onSwitch={() => setMode('signin')} onSuccess={onClose} />
        )}
      </div>
    </div>
  );
}

export function AuthButton() {
  const { user, loading, signout } = useAuth();
  const [showModal, setShowModal] = useState(false);

  if (loading) return null;

  if (user) {
    return (
      <div className={styles.authTrigger}>
        <span className={styles.userDot} />
        <span>{user.name.split(' ')[0]}</span>
        <button className={styles.signoutBtn} onClick={signout}>
          sign out
        </button>
      </div>
    );
  }

  return (
    <>
      <button className={styles.authTrigger} onClick={() => setShowModal(true)}>
        Sign In
      </button>
      {showModal && <AuthModal onClose={() => setShowModal(false)} />}
    </>
  );
}
