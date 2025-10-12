import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivateFn, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';

// @Injectable({
//   providedIn: 'root'
// })
// export class GuardService implements CanActivateFn {

//   constructor() { }

//   canActive(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
//     return true;
//   }
// }

export const canActivateRoute: CanActivateFn = (route: ActivatedRouteSnapshot, state: RouterStateSnapshot) => {
  const token = localStorage.getItem('token');
  if(!token)
    return false;

  const permittedRoles = route.data['permittedRoles'];
  const payload = JSON.parse(atob(token.split('.')[1]));
  const userRoles = payload.roles;

  return userRoles.filter((role: any) => permittedRoles.includes(role)).length > 0;

}