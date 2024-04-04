import { useState } from 'react'
import Card from './components/Card/Card'
import Header from '../src/components/header/index'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className='cards-flex'>
      <Header/>
      <Card/>
    </div>
  )
}

export default App
