import React, { useEffect, useState } from 'react';
import { Table, ButtonToggle } from 'reactstrap';

function App() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = () => {
    fetch("http://localhost:8080/api/users")
      .then(res => res.json())
      .then(
        (result) => {
          setUsers(result.data);
        },
        (error) => {
          console.error('Error fetching users:', error);
        }
      );
  };

  const deleteUser = (id) => {
    // Implement delete user functionality here
    console.log("Delete user with ID:", id);
  };

  return (
    <div className="wrapper">
      <h1>Users List</h1>
      <Table bordered>
        <thead>
          <tr>
            <th>#</th>
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
              <th>{index + 1}</th>
              <td>{user.Name}</td>
              <td>{user.Age}</td>
              <td>{user.DOB}</td>
              <td>{user.Description}</td>
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
