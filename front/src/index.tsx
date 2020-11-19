import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import App from './App';
import './i18n';
import configureStore from './redux/store/configureStore.dev'; //todo: fix for production mode


const persistedState = localStorage.getItem('WSS') //use local storage just to save token
  ? JSON.parse(localStorage.getItem('WSS'))
  : {};

const store = configureStore(persistedState);
store.subscribe(() => {
  const state = store.getState();
  localStorage.setItem(
    'WSS',
    JSON.stringify({
      account: state.Account,
    })
  );
});

ReactDOM.render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>,
  document.getElementById('root')
);