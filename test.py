import streamlit as st
import re
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

class Equation:
    def __init__(self, equation):
        self.equation = equation
        self.coefficients = {'x^2': 0, 'y^2': 0, 'xy': 0, 'x': 0, 'y': 0, 'constant': 0}
    
    def to_lhs(self):
        sides = self.equation.split('=')
        lhs = sides[0].strip()
        rhs = sides[1].strip()
        
        if rhs[0] not in '+-':
            rhs = '+' + rhs
        
        new_rhs = []
        for char in rhs:
            if char == '+':
                new_rhs.append('-')
            elif char == '-':
                new_rhs.append('+')
            else:
                new_rhs.append(char)
        
        self.equation = lhs + ''.join(new_rhs)
    
    def check_equation(self):
        checked_equation = []
        if self.equation[0] in '+-':
            checked_equation.append(self.equation[0])
            self.equation = self.equation[1:]
        if self.equation[0].isalpha():
            checked_equation.append('1')
        
        for i in range(len(self.equation) - 1):
            checked_equation.append(self.equation[i])
            if self.equation[i] in '+-' and self.equation[i+1].isalpha():
                checked_equation.append('1')
        
        checked_equation.append(self.equation[-1])
        self.equation = ''.join(checked_equation)
    
    def pick_terms(self):
        terms = re.findall(r'[+-]?\d*\.?\d*[xy\^2]*', self.equation)
        for term in terms:
            if term:
                self.sort_coefficients(term.strip())
    
    def sort_coefficients(self, term):
        if 'x^2' in term:
            coeff = term.split('x^2')[0]
            self.coefficients['x^2'] += self.get_coefficient_value(coeff)
        elif 'y^2' in term:
            coeff = term.split('y^2')[0]
            self.coefficients['y^2'] += self.get_coefficient_value(coeff)
        elif 'xy' in term:
            coeff = term.split('xy')[0]
            self.coefficients['xy'] += self.get_coefficient_value(coeff)
        elif 'x' in term:
            coeff = term.split('x')[0]
            self.coefficients['x'] += self.get_coefficient_value(coeff)
        elif 'y' in term:
            coeff = term.split('y')[0]
            self.coefficients['y'] += self.get_coefficient_value(coeff)
        else:
            self.coefficients['constant'] += self.get_coefficient_value(term)
    
    def get_coefficient_value(self, coeff):
        if coeff in ('', '+'):
            return 1
        elif coeff == '-':
            return -1
        else:
            return float(coeff)
    
    def give_coefficients(self):
        if '=' in self.equation:
            self.to_lhs()
        self.check_equation()
        self.pick_terms()
        
        return self.coefficients

class ConicSection:
    def __init__(self, coefficients):
        self.A = coefficients['x^2']
        self.B = coefficients['xy']
        self.b = coefficients['y^2']
        self.D = coefficients['x']
        self.E = coefficients['y']
        self.c = coefficients['constant']

    def calculate_conic_section(self):
        h = self.B / 2
        g = self.D / 2
        f = self.E / 2
        
        delta = self.A * self.b * self.c + 2 * f * g * h - self.c * h**2 - self.A * f**2 - self.b * g**2
        
        if self.A == 0 and self.b == 0 and self.B == 0:
            return "Straight Line", self.plot_straight_line()
        elif delta == 0 and self.A != 0 and self.b != 0 and self.B != 0:
            return "Pair of Straight Lines", self.plot_pair_of_straight_lines()
        elif delta != 0 and self.A == self.b and self.B == 0:
            return "Circle", self.plot_circle()
        elif delta != 0 and self.A * self.b - h**2 == 0:
            return "Parabola", self.plot_parabola()
        elif delta != 0 and self.A * self.b - h**2 < 0:
            return "Hyperbola", self.plot_hyperbola()
        elif delta != 0 and self.A * self.b - h**2 > 0:
            return "Ellipse", self.plot_ellipse()
        else:
            return "Invalid input", None

    def plot_straight_line(self):
        x = np.linspace(-10, 10, 400)
        y = (-self.D * x - self.c) / self.E
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(x, y, label='Straight Line')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title('Straight Line')
        ax.axhline(0, color='black',linewidth=0.5)
        ax.axvline(0, color='black',linewidth=0.5)
        ax.grid(color = 'gray', linestyle = '--', linewidth = 0.5)
        ax.legend()
        return fig

    def plot_pair_of_straight_lines(self):
        fig, ax = plt.subplots(figsize=(8, 6))
        
        A = self.A
        B = self.B
        b = self.b
        D = self.D
        E = self.E
        c = self.c
        
        # Calculate the coefficients of the line equations
        det = B**2 - 4 * A * b
        if det == 0:
            x = np.linspace(-10, 10, 400)
            y1 = (-D * x - c) / E
            ax.plot(x, y1, label='Line 1')
        else:
            # Eigenvalues of the quadratic form matrix
            A1 = A
            B1 = B
            C1 = b
            D1 = D
            E1 = E
            F1 = c
            
            # Coefficients of the factored quadratic equation
            coeff = [A1, B1, C1, D1, E1, F1]
            # Find the roots of the factored quadratic equation
            roots = np.roots(coeff)
            x = np.linspace(-10, 10, 400)
            for i, root in enumerate(roots):
                if np.iscomplex(root):
                    continue
                y = root * x + c
                ax.plot(x, y, label=f'Line {i+1}')
        
        ax.axhline(0, color='black',linewidth=0.5)
        ax.axvline(0, color='black',linewidth=0.5)
        ax.grid(color = 'gray', linestyle = '--', linewidth = 0.5)
        ax.legend()
        ax.set_title("Pair of Straight Lines")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        return fig

    def plot_circle(self):
        r = np.sqrt(-self.c / self.A)
        theta = np.linspace(0, 2 * np.pi, 400)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(x, y, label='Circle')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title('Circle')
        ax.axhline(0, color='black',linewidth=0.5)
        ax.axvline(0, color='black',linewidth=0.5)
        ax.grid(color = 'gray', linestyle = '--', linewidth = 0.5)
        ax.legend()
        return fig

    def plot_parabola(self):
        fig, ax = plt.subplots(figsize=(8, 6))
        
        A = self.A
        B = self.B
        C = self.b
        D = self.D
        E = self.E
        F = self.c
        
        if A != 0:  # Parabola opens up or down
            # Convert to standard form y = ax^2 + bx + c
            a = A
            b = D / (2 * A)
            c = (F - b**2 * A) / A
            x = np.linspace(-10, 10, 400)
            y = a * x**2 + b * x + c
            ax.plot(x, y, label='Parabola')
        elif C != 0:  # Parabola opens left or right
            # Convert to standard form x = ay^2 + by + c
            a = C
            b = E / (2 * C)
            c = (F - b**2 * C) / C
            y = np.linspace(-10, 10, 400)
            x = a * y**2 + b * y + c
            ax.plot(x, y, label='Parabola')
        
        ax.axhline(0, color='black', linewidth=0.5)
        ax.axvline(0, color='black', linewidth=0.5)
        ax.grid(color='gray', linestyle='--', linewidth=0.5)
        ax.legend()
        ax.set_title("Parabola")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        return fig

    def plot_hyperbola(self):
        fig, ax = plt.subplots(figsize=(8, 6))
        
        x = np.linspace(-10, 10, 400)
        y1 = np.sqrt((self.c + self.A * x**2) / self.b)
        y2 = -np.sqrt((self.c + self.A * x**2) / self.b)
        
        ax.plot(x, y1, label='Hyperbola')
        ax.plot(x, y2, label='Hyperbola')
        
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title('Hyperbola')
        ax.axhline(0, color='black', linewidth=0.5)
        ax.axvline(0, color='black', linewidth=0.5)
        ax.grid(color='gray', linestyle='--', linewidth=0.5)
        ax.legend()
        return fig

    def plot_ellipse(self):
        fig, ax = plt.subplots(figsize=(8, 6))
        
        h = self.D / (2 * self.A)
        k = self.E / (2 * self.b)
        a = np.sqrt(-self.c / self.A)
        b = np.sqrt(-self.c / self.b)
        
        theta = np.linspace(0, 2 * np.pi, 400)
        x = a * np.cos(theta) + h
        y = b * np.sin(theta) + k
        
        ax.plot(x, y, label='Ellipse')
        
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title('Ellipse')
        ax.axhline(0, color='black', linewidth=0.5)
        ax.axvline(0, color='black', linewidth=0.5)
        ax.grid(color='gray', linestyle='--', linewidth=0.5)
        ax.legend()
        return fig

def main():
    st.title("Conic Section Plotter")
    
    equation_input = st.text_input("Enter the equation (e.g., 'x^2 + y^2 - 1 = 0')", "")
    
    if st.button("Plot"):
        if equation_input:
            eq = Equation(equation_input)
            coefficients = eq.give_coefficients()
            
            conic = ConicSection(coefficients)
            conic_type, fig = conic.calculate_conic_section()
            
            st.write(f"Conic Section Type: {conic_type}")
            
            if fig:
                buf = BytesIO()
                plt.savefig(buf, format="png")
                buf.seek(0)
                st.image(buf, use_column_width=True)
                buf.close()
        else:
            st.warning("Please enter an equation.")

if __name__ == "__main__":
    main()
