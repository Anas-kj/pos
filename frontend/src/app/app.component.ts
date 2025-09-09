import { Component, OnInit } from '@angular/core';
import { PrimeNGConfig, MenuItem } from 'primeng/api';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent implements OnInit {

  menuBarItems: MenuItem[] | undefined;
  sidebarVisible = true;
  menuItems: MenuItem[] | undefined;

  constructor(private primengConfig: PrimeNGConfig) {}

  ngOnInit() {
    this.primengConfig.ripple = true;

    this.menuBarItems = [
      {
          label: '',
          icon: 'pi pi-bars',
          command: () => { this.sidebarVisible = !this.sidebarVisible; }
      },  
      {
          label: 'Quit',
          icon: 'pi pi-fw pi-power-off'
      }
  ];

  this.menuItems = [
    {
        label: 'Employees',
        icon: 'pi pi-users',
        routerLink: '/employees'
    } 
];

  }
  
}
