import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { prisma } from '../config/prisma.js';
import { env } from '../config/env.js';
import { badRequest, unauthorized } from '../utils/httpErrors.js';

const validRoles = ['admin', 'business_user', 'analyst'];

export const signup = async ({ name, email, password, role }) => {
  if (!name || !email || !password) {
    throw badRequest('Name, email, and password are required.');
  }

  if (role && !validRoles.includes(role)) {
    throw badRequest(`Role must be one of: ${validRoles.join(', ')}.`);
  }

  const existingUser = await prisma.user.findUnique({ where: { email } });
  if (existingUser) {
    throw badRequest('A user with this email already exists.');
  }

  const hashedPassword = await bcrypt.hash(password, 12);
  const user = await prisma.user.create({
    data: {
      name,
      email,
      role: role || 'business_user',
      hashedPassword,
    },
  });

  return createAuthResponse(user);
};

export const login = async ({ email, password }) => {
  if (!email || !password) {
    throw badRequest('Email and password are required.');
  }

  const user = await prisma.user.findUnique({ where: { email } });
  if (!user) {
    throw unauthorized('Invalid email or password.');
  }

  const passwordMatch = await bcrypt.compare(password, user.hashedPassword);
  if (!passwordMatch) {
    throw unauthorized('Invalid email or password.');
  }

  return createAuthResponse(user);
};

const createAuthResponse = (user) => {
  const token = jwt.sign(
    {
      sub: user.id,
      email: user.email,
      role: user.role,
      name: user.name,
    },
    env.jwtSecret,
    { expiresIn: '8h' },
  );

  return {
    token,
    user: {
      id: user.id,
      name: user.name,
      email: user.email,
      role: user.role,
    },
  };
};
