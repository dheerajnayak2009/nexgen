import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from scipy.integrate import solve_ivp

class ChargedParticleMotion:
    def __init__(self, q1=1e-6, q2=-1e-6, m1=1e-6, m2=1e-6, 
                 initial_distance=0.1, initial_velocity=0):
        """
        Initialize the two-charge system
        
        Parameters:
        q1, q2: charges in Coulombs
        m1, m2: masses in kg
        initial_distance: initial separation in meters
        initial_velocity: initial velocity magnitude in m/s
        """
        self.q1 = q1
        self.q2 = q2
        self.m1 = m1
        self.m2 = m2
        self.k = 8.99e9  # Coulomb constant
        self.mu0 = 4 * np.pi * 1e-7  # Magnetic constant
        
        # Set up initial positions (along x-axis)
        self.r1_0 = np.array([-initial_distance/2, 0, 0])
        self.r2_0 = np.array([initial_distance/2, 0, 0])
        
        # Initial velocities (perpendicular to separation to create interesting motion)
        self.v1_0 = np.array([0, initial_velocity, 0])
        self.v2_0 = np.array([0, -initial_velocity, 0])
        
    def calculate_forces(self, r1, r2, v1, v2):
        """
        Calculate forces including Coulomb and magnetic components
        Returns forces on particle 1 and particle 2
        """
        # Position vector between charges
        r_vec = r2 - r1
        r_mag = np.linalg.norm(r_vec)
        r_hat = r_vec / (r_mag + 1e-10)  # Avoid division by zero
        
        # Coulomb force
        F_coulomb = self.k * self.q1 * self.q2 / (r_mag**2) * r_hat
        F1_coulomb = F_coulomb
        F2_coulomb = -F_coulomb
        
        # Magnetic field due to moving charge 1 at position of charge 2
        # Biot-Savart: B = (mu0/4pi) * (q * v × r̂) / r²
        v1_cross_r = np.cross(v1, r_hat)
        B1 = (self.mu0 / (4 * np.pi)) * self.q1 * v1_cross_r / (r_mag**2 + 1e-10)
        
        # Magnetic field due to moving charge 2 at position of charge 1
        v2_cross_r_neg = np.cross(v2, -r_hat)
        B2 = (self.mu0 / (4 * np.pi)) * self.q2 * v2_cross_r_neg / (r_mag**2 + 1e-10)
        
        # Magnetic force: F = q * v × B
        F1_magnetic = self.q1 * np.cross(v1, B2)
        F2_magnetic = self.q2 * np.cross(v2, B1)
        
        # Total forces
        F1_total = F1_coulomb + F1_magnetic
        F2_total = F2_coulomb + F2_magnetic
        
        return F1_total, F2_total
    
    def equations_of_motion(self, t, state):
        """
        State vector: [r1x, r1y, r1z, r2x, r2y, r2z, 
                       v1x, v1y, v1z, v2x, v2y, v2z]
        """
        # Extract positions and velocities
        r1 = state[0:3]
        r2 = state[3:6]
        v1 = state[6:9]
        v2 = state[9:12]
        
        # Calculate forces
        F1, F2 = self.calculate_forces(r1, r2, v1, v2)
        
        # Calculate accelerations
        a1 = F1 / self.m1
        a2 = F2 / self.m2
        
        # Return derivatives
        return np.concatenate([v1, v2, a1, a2])
    
    def simulate(self, t_span=(0, 1), t_eval=None):
        """Run simulation"""
        if t_eval is None:
            t_eval = np.linspace(t_span[0], t_span[1], 1000)
        
        # Initial state
        initial_state = np.concatenate([self.r1_0, self.r2_0, self.v1_0, self.v2_0])
        
        # Solve ODE
        solution = solve_ivp(
            self.equations_of_motion, 
            t_span, 
            initial_state, 
            t_eval=t_eval,
            method='RK45',
            rtol=1e-8,
            atol=1e-10
        )
        
        # Extract trajectories
        r1_traj = solution.y[0:3, :].T
        r2_traj = solution.y[3:6, :].T
        t_points = solution.t
        
        return r1_traj, r2_traj, t_points

class ThreeDVisualizer:
    def __init__(self, r1_traj, r2_traj, t_points):
        self.r1_traj = r1_traj
        self.r2_traj = r2_traj
        self.t_points = t_points
        
        # Set up the figure
        self.fig = plt.figure(figsize=(12, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # Calculate limits for axis
        all_points = np.vstack([r1_traj, r2_traj])
        max_range = np.max(np.abs(all_points)) * 1.2
        
        self.ax.set_xlim([-max_range, max_range])
        self.ax.set_ylim([-max_range, max_range])
        self.ax.set_zlim([-max_range, max_range])
        
        # Labels and title
        self.ax.set_xlabel('X (m)', fontsize=12)
        self.ax.set_ylabel('Y (m)', fontsize=12)
        self.ax.set_zlabel('Z (m)', fontsize=12)
        self.ax.set_title('3D Motion of Opposite Charges with Magnetic Effects', fontsize=14)
        
        # Create trajectory lines
        self.traj1_line, = self.ax.plot([], [], [], 'r-', alpha=0.3, label='+q trajectory')
        self.traj2_line, = self.ax.plot([], [], [], 'b-', alpha=0.3, label='-q trajectory')
        
        # Create particle spheres
        self.particle1 = self.create_sphere(center=r1_traj[0], radius=max_range/20, color='red')
        self.particle2 = self.create_sphere(center=r2_traj[0], radius=max_range/20, color='blue')
        
        # Connection line
        self.connection_line, = self.ax.plot([], [], [], 'k--', alpha=0.5, linewidth=1)
        
        # Time display
        self.time_text = self.ax.text2D(0.02, 0.95, '', transform=self.ax.transAxes, 
                                        fontsize=12, color='black')
        
        # Add legend
        self.ax.legend(loc='upper right')
        
        # Add grid
        self.ax.grid(True, alpha=0.3)
        
    def create_sphere(self, center, radius, color, resolution=20):
        """Create a sphere at the given center"""
        u = np.linspace(0, 2 * np.pi, resolution)
        v = np.linspace(0, np.pi, resolution)
        x = center[0] + radius * np.outer(np.cos(u), np.sin(v))
        y = center[1] + radius * np.outer(np.sin(u), np.sin(v))
        z = center[2] + radius * np.outer(np.ones(np.size(u)), np.cos(v))
        
        return self.ax.plot_surface(x, y, z, color=color, alpha=0.7, rstride=1, cstride=1)
    
    def update_sphere(self, sphere, new_center, radius):
        """Update sphere position"""
        sphere.remove()
        new_sphere = self.create_sphere(new_center, radius, sphere.get_facecolors()[0][:3])
        return new_sphere
    
    def animate_frame(self, frame):
        """Update animation for each frame"""
        # Update particle positions
        r1 = self.r1_traj[frame]
        r2 = self.r2_traj[frame]
        
        # Update spheres
        self.particle1 = self.update_sphere(self.particle1, r1, 
                                            np.max(np.abs(self.r1_traj))*0.05)
        self.particle2 = self.update_sphere(self.particle2, r2, 
                                            np.max(np.abs(self.r2_traj))*0.05)
        
        # Update trajectories
        self.traj1_line.set_data(self.r1_traj[:frame+1, 0], self.r1_traj[:frame+1, 1])
        self.traj1_line.set_3d_properties(self.r1_traj[:frame+1, 2])
        
        self.traj2_line.set_data(self.r2_traj[:frame+1, 0], self.r2_traj[:frame+1, 1])
        self.traj2_line.set_3d_properties(self.r2_traj[:frame+1, 2])
        
        # Update connection line
        self.connection_line.set_data([r1[0], r2[0]], [r1[1], r2[1]])
        self.connection_line.set_3d_properties([r1[2], r2[2]])
        
        # Update time display
        self.time_text.set_text(f'Time: {self.t_points[frame]:.3f} s')
        
        return [self.particle1, self.particle2, self.traj1_line, 
                self.traj2_line, self.connection_line, self.time_text]
    
    def animate(self, interval=20):
        """Create animation"""
        anim = FuncAnimation(self.fig, self.animate_frame, 
                           frames=len(self.t_points), interval=interval, 
                           blit=False, repeat=True)
        plt.show()
        return anim
    
    def plot_trajectories(self):
        """Plot 3D trajectories"""
        self.ax.plot3D(self.r1_traj[:, 0], self.r1_traj[:, 1], self.r1_traj[:, 2], 
                      'r-', linewidth=1, alpha=0.5, label='+q')
        self.ax.plot3D(self.r2_traj[:, 0], self.r2_traj[:, 1], self.r2_traj[:, 2], 
                      'b-', linewidth=1, alpha=0.5, label='-q')
        self.ax.legend()
        plt.show()

def main():
    # Parameters
    q = 1e-6  # 1 microCoulomb
    m = 1e-6  # 1 mg
    distance = 0.05  # 5 cm
    init_velocity = 0.01  # 1 cm/s initial perpendicular velocity
    
    # Create simulation
    simulation = ChargedParticleMotion(
        q1=q, q2=-q,
        m1=m, m2=m,
        initial_distance=distance,
        initial_velocity=init_velocity
    )
    
    # Run simulation
    print("Simulating charge motion...")
    r1_traj, r2_traj, t_points = simulation.simulate(t_span=(0, 0.5))
    
    # Visualize
    print("Creating visualization...")
    visualizer = ThreeDVisualizer(r1_traj, r2_traj, t_points)
    
    # Show animation
    print("Starting animation...")
    visualizer.animate(interval=20)  # 20ms between frames
    
    # Print some information
    final_distance = np.linalg.norm(r1_traj[-1] - r2_traj[-1])
    print(f"\nSimulation complete!")
    print(f"Initial separation: {distance:.3f} m")
    print(f"Final separation: {final_distance:.3f} m")
    print(f"Time span: {t_points[-1]:.3f} s")

if __name__ == "__main__":
    main()