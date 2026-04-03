import { Injectable } from '@nestjs/common';

@Injectable()
export class AuthService {
  private readonly user = {
    id: 'user_1',
    name: 'Avery Chen',
    email: 'avery@northwind.ai',
    role: 'owner',
  };

  login(email: string, _password: string) {
    return {
      token: 'demo-token',
      user: { ...this.user, email },
    };
  }

  currentUser() {
    return this.user;
  }
}
