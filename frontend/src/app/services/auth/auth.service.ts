import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { baseUrl } from 'src/models/baseUrl';
import { LoginToken } from 'src/models/interfaces/LoginToken';
import { BaseOut } from 'src/models/interfaces/baseOut';
import { ConfirmAccount } from 'src/models/interfaces/confirmAccount';
import { ForgetPassword } from 'src/models/interfaces/forgetPassword';
import { Login } from 'src/models/interfaces/login';
import { ResetPassword } from 'src/models/interfaces/resetPassword';

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
  
  resetPassword(form: ResetPassword){
    const endPointUrl = baseUrl + 'resetPassword';
    return this.http.patch<BaseOut>(endPointUrl, form);
  }

  confirmAccount(form: ConfirmAccount){
    const endPointUrl = baseUrl + 'confirmAccount';
    return this.http.patch<BaseOut>(endPointUrl, form);
  }
}
