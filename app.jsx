import React, { useState, useEffect, useMemo } from 'react';
import { initializeApp } from 'firebase/app';
import { 
  getAuth, 
  signInAnonymously, 
  signInWithCustomToken, 
  onAuthStateChanged 
} from 'firebase/auth';
import { 
  getFirestore, 
  collection, 
  doc, 
  setDoc, 
  getDoc,
  getDocs,
  addDoc, 
  deleteDoc, 
  onSnapshot, 
  serverTimestamp 
} from 'firebase/firestore';
import { 
  Layout, 
  Plus, 
  Trash2, 
  LogOut, 
  Calendar, 
  Wallet, 
  Building2, 
  History,
  Clock,
  User,
  Lock,
  ArrowRight,
  TrendingUp,
  CreditCard,
  UserPlus,
  LogIn,
  BookOpen,
  PieChart,
  BarChart3
} from 'lucide-react';

// --- Firebase Configuration ---
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'payroll-calc-v2';

// Constants
const MEIKO_KOMA_NAME = '明光義塾 (コマ給)';
const MEIKO_KOMA_PRICE = 2448;
const MEIKO_KOMA_MINUTES = 115; // 1h 55m

export default function App() {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [loginForm, setLoginForm] = useState({ id: '', password: '' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [view, setView] = useState('dashboard');
  const [workplaces, setWorkplaces] = useState([]);
  const [shifts, setShifts] = useState([]);
  const [logs, setLogs] = useState([]);

  // Auth initialization
  useEffect(() => {
    const initAuth = async () => {
      try {
        if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
          await signInWithCustomToken(auth, __initial_auth_token);
        } else {
          await signInAnonymously(auth);
        }
      } catch (error) {
        console.error("Auth error:", error);
      }
    };
    initAuth();
    const unsubscribe = onAuthStateChanged(auth, (u) => {
      setUser(u);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  // Seed initial data for Meiko Gijuku
  useEffect(() => {
    if (!user || !isAuthenticated) return;

    const seedData = async () => {
      const wpRef = collection(db, 'artifacts', appId, 'users', user.uid, 'workplaces');
      const snapshot = await getDocs(wpRef);
      
      if (snapshot.empty) {
        const meikoKomaRate = MEIKO_KOMA_PRICE / (MEIKO_KOMA_MINUTES / 60);
        const initialWps = [
          { name: MEIKO_KOMA_NAME, hourlyRate: meikoKomaRate },
          { name: '明光義塾 (事務給)', hourlyRate: 1226 }
        ];

        for (const wp of initialWps) {
          await addDoc(wpRef, { ...wp, createdAt: serverTimestamp() });
        }
        recordLog('初期設定', '明光義塾のデータを自動登録しました');
      }
    };
    seedData();
  }, [user, isAuthenticated]);

  // Firestore listeners
  useEffect(() => {
    if (!user || !isAuthenticated) return;

    const wpRef = collection(db, 'artifacts', appId, 'users', user.uid, 'workplaces');
    const shiftRef = collection(db, 'artifacts', appId, 'users', user.uid, 'shifts');
    const logRef = collection(db, 'artifacts', appId, 'users', user.uid, 'action_logs');

    const unsubWp = onSnapshot(wpRef, (snapshot) => {
      setWorkplaces(snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() })));
    });

    const unsubShifts = onSnapshot(shiftRef, (snapshot) => {
      setShifts(snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() })));
    });

    const unsubLogs = onSnapshot(logRef, (snapshot) => {
      const sortedLogs = snapshot.docs
        .map(doc => ({ id: doc.id, ...doc.data() }))
        .sort((a, b) => b.timestamp?.seconds - a.timestamp?.seconds);
      setLogs(sortedLogs);
    });

    return () => {
      unsubWp();
      unsubShifts();
      unsubLogs();
    };
  }, [user, isAuthenticated]);

  // Logging
  const recordLog = async (action, details) => {
    if (!user) return;
    try {
      await addDoc(collection(db, 'artifacts', appId, 'users', user.uid, 'action_logs'), {
        action,
        details,
        timestamp: serverTimestamp()
      });
    } catch (e) { console.error(e); }
  };

  // Complex Analytics
  const stats = useMemo(() => {
    const now = new Date();
    const curM = now.getMonth();
    const curY = now.getFullYear();

    let monthTotal = 0;
    let yearTotal = 0;
    const dailyMap = {};
    const workplaceStats = {}; // { wpId: { name, month, year } }

    // Initialize workplaceStats
    workplaces.forEach(wp => {
      workplaceStats[wp.id] = { name: wp.name, month: 0, year: 0 };
    });

    shifts.forEach(shift => {
      const wp = workplaces.find(w => w.id === shift.workplaceId);
      if (!wp) return;

      const amount = Math.round(shift.hours * wp.hourlyRate);
      const sDate = new Date(shift.date);
      const isCurY = sDate.getFullYear() === curY;
      const isCurM = isCurY && sDate.getMonth() === curM;

      // Overall totals
      if (isCurY) yearTotal += amount;
      if (isCurM) monthTotal += amount;

      // Workplace specific totals
      if (workplaceStats[shift.workplaceId]) {
        if (isCurY) workplaceStats[shift.workplaceId].year += amount;
        if (isCurM) workplaceStats[shift.workplaceId].month += amount;
      }

      // Daily grouping
      dailyMap[shift.date] = (dailyMap[shift.date] || 0) + amount;
    });

    const dailyList = Object.keys(dailyMap)
      .sort((a, b) => b.localeCompare(a))
      .map(date => ({ date, amount: dailyMap[date] }));

    return { 
      monthTotal, 
      yearTotal, 
      dailyList, 
      workplaceBreakdown: Object.values(workplaceStats) 
    };
  }, [shifts, workplaces]);

  const handleAuth = async (e) => {
    e.preventDefault();
    setError('');
    const { id, password } = loginForm;
    if (!id || !password) { setError('IDとパスワードを入力してください'); return; }
    const credRef = doc(db, 'artifacts', appId, 'public', 'data', 'credentials', id);
    try {
      if (isRegisterMode) {
        const docSnap = await getDoc(credRef);
        if (docSnap.exists()) { setError('このIDは既に使用されています'); return; }
        await setDoc(credRef, { password, createdAt: serverTimestamp() });
        setIsAuthenticated(true);
      } else {
        const docSnap = await getDoc(credRef);
        if (docSnap.exists() && docSnap.data().password === password) {
          setIsAuthenticated(true);
        } else { setError('IDまたはパスワードが正しくありません'); }
      }
    } catch (err) { setError('エラーが発生しました'); }
  };

  if (loading) return <div className="flex items-center justify-center min-h-screen bg-slate-50 text-slate-400 font-bold">Initializing...</div>;

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-white rounded-[2.5rem] shadow-2xl border border-slate-100 p-8 md:p-12 animate-in fade-in zoom-in-95 duration-500">
          <div className="flex justify-center mb-8">
            <div className="w-20 h-20 bg-blue-600 rounded-3xl flex items-center justify-center shadow-lg rotate-3"><Wallet size={40} className="text-white -rotate-3" /></div>
          </div>
          <h1 className="text-3xl font-black text-slate-800 text-center mb-2">{isRegisterMode ? 'Create Account' : 'Welcome Back'}</h1>
          <p className="text-slate-400 text-center mb-8 font-medium">給与管理システムへようこそ</p>
          {error && <div className="mb-6 p-4 bg-red-50 text-red-600 text-sm font-bold rounded-2xl border border-red-100">{error}</div>}
          <form onSubmit={handleAuth} className="space-y-4">
            <div className="relative"><User className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-300" size={20} /><input type="text" placeholder="ログインID" className="w-full pl-12 pr-4 py-4 bg-slate-50 border-none rounded-2xl focus:ring-2 focus:ring-blue-500 outline-none font-medium" value={loginForm.id} onChange={(e) => setLoginForm({...loginForm, id: e.target.value})} /></div>
            <div className="relative"><Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-300" size={20} /><input type="password" placeholder="パスワード" className="w-full pl-12 pr-4 py-4 bg-slate-50 border-none rounded-2xl focus:ring-2 focus:ring-blue-500 outline-none font-medium" value={loginForm.password} onChange={(e) => setLoginForm({...loginForm, password: e.target.value})} /></div>
            <button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-2xl shadow-xl transition-all flex items-center justify-center gap-2 group mt-2">{isRegisterMode ? 'アカウントを作成' : 'ログイン開始'} <LogIn size={20} /></button>
          </form>
          <div className="mt-8 text-center"><button onClick={() => {setIsRegisterMode(!isRegisterMode); setError('');}} className="text-sm font-bold text-blue-600 underline underline-offset-4">{isRegisterMode ? '既にアカウントをお持ちの方' : '新しくアカウントを作成する'}</button></div>
        </div>
      </div>
    );
  }

  // Views
  const Dashboard = () => (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Overall Summary Cards */}
      <section>
        <h2 className="text-sm font-black text-slate-400 uppercase tracking-widest px-2 mb-4 flex items-center gap-2">
          <PieChart size={16} /> 総合収支サマリー
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gradient-to-br from-blue-600 to-indigo-700 p-8 rounded-[2rem] text-white shadow-xl shadow-blue-100">
            <div className="flex items-center justify-between mb-4"><span className="text-blue-100 text-sm font-bold uppercase tracking-wider">Total Monthly</span><TrendingUp size={20} /></div>
            <div className="text-4xl font-black mb-1">¥{stats.monthTotal.toLocaleString()}</div>
            <div className="text-blue-200 text-xs font-medium underline decoration-blue-400 underline-offset-4">全勤務先 総合月間金額</div>
          </div>
          <div className="bg-white p-8 rounded-[2rem] border border-slate-100 shadow-xl shadow-slate-100">
            <div className="flex items-center justify-between mb-4"><span className="text-slate-400 text-sm font-bold uppercase tracking-wider">Total Yearly</span><Calendar size={20} /></div>
            <div className="text-4xl font-black text-slate-800 mb-1">¥{stats.yearTotal.toLocaleString()}</div>
            <div className="text-slate-400 text-xs font-medium underline decoration-slate-200 underline-offset-4">全勤務先 総合年間金額</div>
          </div>
        </div>
      </section>

      {/* Breakdown per Workplace */}
      <section>
        <h2 className="text-sm font-black text-slate-400 uppercase tracking-widest px-2 mb-4 flex items-center gap-2">
          <BarChart3 size={16} /> 勤務先別 収支詳細
        </h2>
        <div className="grid grid-cols-1 gap-4">
          {stats.workplaceBreakdown.map((wp, idx) => (
            <div key={idx} className="bg-white p-6 rounded-[1.5rem] border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center font-bold">
                  <Building2 size={20} />
                </div>
                <h3 className="font-black text-slate-800 text-lg">{wp.name}</h3>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-50 p-4 rounded-2xl">
                  <div className="text-[10px] font-black text-slate-400 uppercase mb-1">月間収益</div>
                  <div className="text-xl font-black text-slate-700">¥{wp.month.toLocaleString()}</div>
                </div>
                <div className="bg-slate-50 p-4 rounded-2xl">
                  <div className="text-[10px] font-black text-slate-400 uppercase mb-1">年間収益</div>
                  <div className="text-xl font-black text-slate-700">¥{wp.year.toLocaleString()}</div>
                </div>
              </div>
            </div>
          ))}
          {stats.workplaceBreakdown.length === 0 && (
            <div className="text-center py-10 bg-white rounded-3xl border border-dashed border-slate-200 text-slate-400">
              勤務先データがありません
            </div>
          )}
        </div>
      </section>

      {/* Daily List (Quick View) */}
      <section className="space-y-4">
        <h2 className="text-sm font-black text-slate-400 uppercase tracking-widest px-2 flex items-center gap-2">
          <CreditCard size={16} /> 最近の日別収益
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {stats.dailyList.slice(0, 4).map((day, idx) => (
            <div key={idx} className="bg-white p-5 rounded-3xl border border-slate-100 flex justify-between items-center shadow-sm">
              <div><div className="text-xs font-bold text-slate-400 mb-1">{day.date}</div><div className="text-lg font-black text-slate-700">¥{day.amount.toLocaleString()}</div></div>
              <div className="h-10 w-1 bg-blue-500 rounded-full"></div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );

  const WorkplacesView = () => {
    const [name, setName] = useState('');
    const [rate, setRate] = useState('');
    const addWorkplace = async (e) => {
      e.preventDefault(); if (!name || !rate) return;
      await addDoc(collection(db, 'artifacts', appId, 'users', user.uid, 'workplaces'), { name, hourlyRate: Number(rate), createdAt: serverTimestamp() });
      recordLog('勤務先追加', `${name}`);
      setName(''); setRate('');
    };
    return (
      <div className="space-y-8">
        <form onSubmit={addWorkplace} className="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-xl space-y-6">
          <h2 className="font-black text-2xl text-slate-800">勤務先登録</h2>
          <div className="grid grid-cols-1 gap-4">
            <input type="text" placeholder="Workplace Name" className="w-full p-4 rounded-2xl bg-slate-50 border-none font-bold outline-none focus:ring-2 focus:ring-blue-500" value={name} onChange={(e) => setName(e.target.value)} />
            <input type="number" placeholder="Hourly Rate (JPY)" className="w-full p-4 rounded-2xl bg-slate-50 border-none font-bold outline-none focus:ring-2 focus:ring-blue-500" value={rate} onChange={(e) => setRate(e.target.value)} />
          </div>
          <button type="submit" className="w-full bg-slate-900 text-white font-black py-4 rounded-2xl flex items-center justify-center gap-2 shadow-lg"><Plus size={20} /> Register</button>
        </form>
        <div className="grid gap-3">
          {workplaces.map(wp => (
            <div key={wp.id} className="bg-white p-5 rounded-3xl border border-slate-100 flex justify-between items-center shadow-sm">
              <div className="flex items-center gap-4"><div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center"><Building2 size={24} /></div><div><div className="font-black text-slate-800">{wp.name}</div><div className="text-sm font-bold text-slate-400">¥{wp.hourlyRate.toLocaleString()} / hr</div></div></div>
              <button onClick={async () => { await deleteDoc(doc(db, 'artifacts', appId, 'users', user.uid, 'workplaces', wp.id)); recordLog('勤務先削除', wp.name); }} className="p-3 text-slate-200 hover:text-red-500 transition-all"><Trash2 size={20} /></button>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const ShiftsView = () => {
    const [wpId, setWpId] = useState('');
    const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
    const [hours, setHours] = useState('');
    const [komaCount, setKomaCount] = useState('1');

    const selectedWp = workplaces.find(w => w.id === wpId);
    const isMeikoKoma = selectedWp?.name === MEIKO_KOMA_NAME;

    const addShift = async (e) => {
      e.preventDefault();
      if (!wpId || !date) return;
      let finalH = isMeikoKoma ? (Number(komaCount) * MEIKO_KOMA_MINUTES) / 60 : Number(hours);
      if (!finalH || finalH <= 0) return;
      await addDoc(collection(db, 'artifacts', appId, 'users', user.uid, 'shifts'), {
        workplaceId: wpId, date, hours: finalH, createdAt: serverTimestamp()
      });
      recordLog('シフト登録', `${selectedWp.name}`);
      setHours('');
    };

    return (
      <div className="space-y-8">
        <form onSubmit={addShift} className="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-xl space-y-6">
          <h2 className="font-black text-2xl text-slate-800 text-center">シフト追加</h2>
          <div className="space-y-4">
            <select className="w-full p-4 rounded-2xl bg-slate-50 border-none outline-none focus:ring-2 focus:ring-blue-500 font-bold" value={wpId} onChange={(e) => setWpId(e.target.value)}>
              <option value="">勤務先を選択</option>
              {workplaces.map(wp => <option key={wp.id} value={wp.id}>{wp.name}</option>)}
            </select>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input type="date" className="p-4 rounded-2xl bg-slate-50 border-none font-bold" value={date} onChange={(e) => setDate(e.target.value)} />
              {isMeikoKoma ? (
                <select className="w-full p-4 rounded-2xl bg-blue-50 border-none font-black text-blue-700" value={komaCount} onChange={(e) => setKomaCount(e.target.value)}>
                  {[1,2,3,4,5,6].map(n => <option key={n} value={n}>{n} コマ</option>)}
                </select>
              ) : (
                <input type="number" step="0.1" placeholder="時間(h)" className="p-4 rounded-2xl bg-slate-50 border-none font-bold" value={hours} onChange={(e) => setHours(e.target.value)} />
              )}
            </div>
          </div>
          <button type="submit" className="w-full bg-blue-600 text-white font-black py-4 rounded-2xl flex items-center justify-center gap-2 shadow-xl active:scale-95 transition-all"><Plus size={20} /> Add Shift</button>
        </form>
        <div className="grid gap-3">
          {shifts.sort((a,b) => b.date.localeCompare(a.date)).map(shift => {
            const wp = workplaces.find(w => w.id === shift.workplaceId);
            const isMeiko = wp?.name === MEIKO_KOMA_NAME;
            return (
              <div key={shift.id} className="bg-white p-5 rounded-3xl border border-slate-100 flex justify-between items-center shadow-sm">
                <div className="flex items-center gap-4"><div className="w-12 h-12 bg-emerald-50 text-emerald-600 rounded-2xl flex items-center justify-center"><Clock size={24} /></div><div><div className="font-black text-slate-800">{wp?.name || '不明'}</div><div className="text-xs font-bold text-slate-400 uppercase">{shift.date} • {isMeiko ? Math.round(shift.hours / (MEIKO_KOMA_MINUTES/60)) + ' コマ' : shift.hours + ' h'}</div></div></div>
                <div className="flex items-center gap-4"><div className="text-right font-black text-slate-700 text-lg">¥{Math.round(shift.hours * (wp?.hourlyRate || 0)).toLocaleString()}</div><button onClick={async () => { await deleteDoc(doc(db, 'artifacts', appId, 'users', user.uid, 'shifts', shift.id)); recordLog('シフト削除', shift.id); }} className="p-2 text-slate-200 hover:text-red-500 transition-colors"><Trash2 size={18} /></button></div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-slate-50 pb-32 md:pb-12 flex flex-col items-center">
      <header className="w-full max-w-2xl bg-white/70 backdrop-blur-xl border-b border-slate-100 p-6 sticky top-0 z-30 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg"><Wallet size={20} className="text-white" /></div>
          <h1 className="text-xl font-black text-slate-800 tracking-tight">Payroll<span className="text-blue-600">Pro</span></h1>
        </div>
        <button onClick={() => setIsAuthenticated(false)} className="p-2 text-slate-400 hover:text-slate-800 transition-colors"><LogOut size={22} /></button>
      </header>
      <main className="w-full max-w-2xl p-6 flex-1">
        {view === 'dashboard' && <Dashboard />}
        {view === 'workplaces' && <WorkplacesView />}
        {view === 'shifts' && <ShiftsView />}
        {view === 'logs' && <div className="space-y-4">{logs.map(log => (
          <div key={log.id} className="bg-white p-5 rounded-3xl border border-slate-50 flex gap-4"><div className="w-2 h-2 rounded-full bg-blue-500 mt-2 flex-shrink-0"></div><div><div className="text-[10px] font-black text-slate-300 uppercase mb-1">{log.timestamp?.toDate().toLocaleString()}</div><div className="font-black text-slate-700 text-sm">{log.action}</div><div className="text-slate-400 text-xs mt-1">{log.details}</div></div></div>
        ))}</div>}
      </main>
      <nav className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-slate-900/95 backdrop-blur-md text-white rounded-full px-8 py-4 flex items-center gap-10 shadow-2xl z-40 border border-white/10">
        {[ {id:'dashboard', icon:Layout}, {id:'workplaces', icon:Building2}, {id:'shifts', icon:Calendar}, {id:'logs', icon:History} ].map(item => (
          <button key={item.id} onClick={() => setView(item.id)} className={`relative p-2 transition-all ${view === item.id ? 'text-blue-400 scale-110' : 'text-slate-500 hover:text-slate-300'}`}><item.icon size={24} />{view === item.id && <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 bg-blue-400 rounded-full"></span>}</button>
        ))}
      </nav>
    </div>
  );
}
