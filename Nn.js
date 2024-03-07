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

const Profile = ({ onSubmit, src, name, age, dob, description }) => (
  <div className="profile-editing-container">
    <h1>Edit Profile</h1>
    <form onSubmit={onSubmit}>
      <div className="form-group">
        <label htmlFor="name">Name:</label>
        <input type="text" id="name" value={name} onChange={e => onChange(e, 'name')} />
      </div>
      <div className="form-group">
        <label htmlFor="age">Age:</label>
        <input type="number" id="age" value={age} onChange={e => onChange(e, 'age')} />
      </div>
      <div className="form-group">
        <label htmlFor="dob">Date of Birth:</label>
        <input type="date" id="dob" value={dob} onChange={e => onChange(e, 'dob')} />
      </div>
      <div className="form-group">
        <label htmlFor="description">Description:</label>
        <textarea id="description" value={description} onChange={e => onChange(e, 'description')} />
      </div>
      <div className="form-group">
        <label htmlFor="image">Profile Picture:</label>
        <ImgUpload onChange={onChange} src={src} />
      </div>
      <button type="submit" className="btn btn-primary">
        Save Changes
      </button>
    </form>
    <ToastContainer />
  </div>
);

export default function ProfileEditingPage() {
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

  const handleChange = (e, field) => {
    const value = e.target.value;
    switch (field) {
      case 'name':
        setName(value);
        break;
      case 'age':
        setAge(value);
        break;
      case 'dob':
        setDob(value);
        break;
      case 'description':
        setDescription(value);
        break;
      default:
        break;
    }
  };

  return (
    <Profile
      onSubmit={handleSubmit}
      src={image ? URL.createObjectURL(image) : ''}
      name={name}
      age={age}
      dob={dob}
      description={description}
      onChange={handleChange}
    />
  );
}
