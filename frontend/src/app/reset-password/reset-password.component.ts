import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../services/auth/auth.service';
import { MessageService } from 'primeng/api';
import { ResetPassword } from 'src/models/interfaces/resetPassword';
import { ActivatedRoute, Router } from '@angular/router';
import { BaseOut } from 'src/models/interfaces/baseOut';

@Component({
  selector: 'app-reset-password',
  templateUrl: './reset-password.component.html',
  styleUrls: ['./reset-password.component.css']
})
export class ResetPasswordComponent {
  resetPasswordForm = this.fb.group({
    password: [null, Validators.required],
    confirm_password: [null, Validators.required],
  }, {
    validators: [this.passwordMatch()]
  });;
 
  constructor(
    private authService: AuthService, 
    public messageService: MessageService,
    private fb: FormBuilder,
    private router: Router,
    private activatedRoute: ActivatedRoute
  ) {}

  passwordMatch() {
    return (formGroup: FormGroup) => {
      const password = formGroup.controls['password'];
      const confirm_password = formGroup.controls['confirm_password'];

      if(confirm_password.errors && !confirm_password.errors['passwordMatch']) {
        return;
      }
      if(password.value !== confirm_password.value) {
        confirm_password.setErrors({ passwordMatch: true });
      } else {
        confirm_password.setErrors(null);
      }
    };
  }

  deepCopy(obj: any) {
    return JSON.parse(JSON.stringify(obj));
  }

  onSubmit() {
    const form: ResetPassword = this.deepCopy(this.resetPasswordForm.value)
    this.activatedRoute.queryParams.subscribe((params) => {
      form.reset_code = params['reset_code'];
    });

    this.authService.resetPassword(form).subscribe(
      (data: BaseOut) => {
        const success = data.status_code === 200;
        const severity = success ? 'success' : 'error';
        this.messageService.add({severity, summary: severity, detail: data.detail});
        
        if(success){
          this.router.navigate(['/login']);
        }
      });
  }






}
