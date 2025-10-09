import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { baseUrl } from 'src/models/baseUrl';
import { LoginToken } from 'src/models/interfaces/LoginToken';
import { ForgetPassword } from 'src/models/interfaces/forgetPassword';
import { Login } from 'src/models/interfaces/login';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor(private http: HttpClient) { }


  login(form: Login) {
    let params = new HttpParams()
      .set('username', form.username)
      .set('password', form.password)
    
    const httpOptions = params
    const endPointUrl = baseUrl + 'token';
    return this.http.post<LoginToken>(endPointUrl, httpOptions);
  }

  forgetPassword(form: ForgetPassword) {
    const endPointUrl = baseUrl + 'forgetPassword';
    return this.http.post<LoginToken>(endPointUrl, form);
  }
  
}
