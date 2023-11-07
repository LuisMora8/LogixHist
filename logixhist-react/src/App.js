import Listgroup from '../src/components/Listgroup.jsx';
import Graph from '../src/components/Graph.jsx';
import logo from './logo.svg';
import './App.css';

function App(props) {
  const subject = props.subject;
  const device_objects = [
    'TestPLC',
    'test_device',
    'Device_3',
    'TestPLC',
    'test_device',
    'Device_3',
    'Device_3',
    'TestPLC',
    'test_device'
  ];
  const tag_objects = [
    'string1',
    'bool1',
    'int1',
    'dint1',
    'float1',
    'string2',
    'bool2',
    'int2',
    'dint2',
    'float2',
  ];
  return (
    <div className="App">
      <div className='Sidebar'>
        <Listgroup items={device_objects} ></Listgroup>
        <Listgroup items={tag_objects} ></Listgroup>
      </div>
      <div className='Graph'>
        <Graph></Graph>
      </div>
    </div>
  );
}

export default App;
