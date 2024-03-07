import React, { useEffect, useState } from 'react';
import { Table, ButtonToggle, Input } from 'reactstrap';
import './hook.css';

function App() {
  const [users, setUsers] = useState([
    { ID: 1, Name: 'John Doe', Age: '30', DOB: '1992-05-15', Description: 'Software Engineer' },
    { ID: 2, Name: 'Alice Smith', Age: '25', DOB: '1997-10-22', Description: 'Web Developer' },
    { ID: 3, Name: 'Bob Johnson', Age: '35', DOB: '1987-03-10', Description: 'Data Analyst' },
    { ID: 4, Name: 'Eve Brown', Age: '28', DOB: '1994-08-03', Description: 'Graphic Designer' },
    { ID: 5, Name: 'Charlie Williams', Age: '32', DOB: '1990-12-28', Description: 'Marketing Manager' }
  ]);

  const handleEdit = (id, field, value) => {
    const updatedUsers = users.map(user => {
      if (user.ID === id) {
        return { ...user, [field]: value };
      }
      return user;
    });
    setUsers(updatedUsers);
  };

  const deleteUser = (id) => {
    const updatedUsers = users.filter(user => user.ID !== id);
    setUsers(updatedUsers);
  };

  return (
    <div className="wrapper">
      <h1>Users List</h1>
      <Table bordered>
        <thead>
          <tr>
            <th>Name</th>
            <th>Age</th>
            <th>DOB</th>
            <th>Description</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user, index) => (
            <tr key={user.ID}>
              <td>
                <Input type="text" value={user.Name} onChange={(e) => handleEdit(user.ID, 'Name', e.target.value)} />
              </td>
              <td>
                <Input type="text" value={user.Age} onChange={(e) => handleEdit(user.ID, 'Age', e.target.value)} />
              </td>
              <td>
                <Input type="text" value={user.DOB} onChange={(e) => handleEdit(user.ID, 'DOB', e.target.value)} />
              </td>
              <td>
                <Input type="text" value={user.Description} onChange={(e) => handleEdit(user.ID, 'Description', e.target.value)} />
              </td>
              <td>
                <ButtonToggle color="warning" onClick={() => console.log("Edit user:", user.ID)}>Edit</ButtonToggle>{' '}
                <ButtonToggle color="danger" onClick={() => deleteUser(user.ID)}>Delete</ButtonToggle>{' '}
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
}

export default App;
