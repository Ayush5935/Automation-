import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const ImgUpload = ({ onChange, src }) => (
  <label htmlFor="photo-upload" className="custom-file-upload fas">
    <div className="img-wrap img-upload">
      <img src={src} alt="Preview" />
    </div>
    <input id="photo-upload" type="file" onChange={onChange} />
  </label>
);

const Name = ({ onChange, value }) => (
  <div className="field">
    <label htmlFor="name">Name:</label>
    <input
      id="name"
      type="text"
      onChange={onChange}
      maxLength="25"
      value={value}
      placeholder="Alexa"
      required
    />
  </div>
);

const Status = ({ onChange, value }) => (
  <div className="field">
    <label htmlFor="status">Status:</label>
    <input
      id="status"
      type="text"
      onChange={onChange}
      maxLength="35"
      value={value}
      placeholder="It's a nice day!"
      required
    />
  </div>
);

const Profile = ({ onSubmit, name, status }) => (
  <div className="card">
    <form onSubmit={onSubmit}>
      <h1>Profile Card</h1>
      <div className="name">{name}</div>
      <div className="status">{status}</div>
      <button type="submit" className="edit">
        Edit Profile
      </button>
    </form>
  </div>
);

const Edit = ({ onSubmit, children }) => (
  <div className="card">
    <form onSubmit={onSubmit}>
      <h1>Profile Card</h1>
      {children}
      <button type="submit" className="save">
        Save
      </button>
    </form>
  </div>
);

const ProfileEditingPage = () => {
  const [name, setName] = useState('');
  const [image, setImage] = useState(null);
  const [age, setAge] = useState('');
  const [dob, setDob] = useState('');
  const [description, setDescription] = useState('');

  useEffect(() => {
    // Fetch user's existing details
    axios.get('/api/user/profile')
      .then(response => {
        const { name, age, dob, description } = response.data;
        setName(name);
        setAge(age);
        setDob(dob);
        setDescription(description);
      })
      .catch(error => {
        console.log('Error fetching user profile:', error);
      });
  }, []);

  const handleImageChange = (e) => {
    setImage(e.target.files[0]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('name', name);
    formData.append('image', image);
    formData.append('age', age);
    formData.append('dob', dob);
    formData.append('description', description);

    axios.post('/api/user/profile/update', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
      .then(response => {
        console.log('Profile updated successfully:', response.data);
        toast.success('Profile updated successfully');
      })
      .catch(error => {
        console.error('Error updating profile:', error);
        toast.error('Error updating profile');
      });
  };

  return (
    <div className="profile-editing-container">
      <h1>Edit Profile</h1>
      <form onSubmit={handleSubmit}>
        <Name onChange={(e) => setName(e.target.value)} value={name} />
        <ImgUpload onChange={handleImageChange} src={image} />
        <div className="form-group">
          <label htmlFor="age">Age:</label>
          <input type="number" id="age" value={age} onChange={(e) => setAge(e.target.value)} />
        </div>
        <div className="form-group">
          <label htmlFor="dob">Date of Birth:</label>
          <input type="date" id="dob" value={dob} onChange={(e) => setDob(e.target.value)} />
        </div>
        <div className="form-group">
          <label htmlFor="description">Description:</label>
          <textarea id="description" value={description} onChange={(e) => setDescription(e.target.value)} />
        </div>
        <button type="submit" className="btn btn-primary">Save Changes</button>
      </form>
      <ToastContainer />
    </div>
  );
};

export default ProfileEditingPage;
