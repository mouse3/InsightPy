## Para M-PSK
En una modulación PSK, solo se juega con la fase de la onda senoidal $\theta$ y aquí $V=1$

Teniendo que una onda senoidal se define matemáticamente como $Vsin(ft+\theta)=A$
Donde A es la amplitud de salida y $V$ es la amplitud de entrada(siéntete orgulloso si entiendes esto).

Entonces: $$\theta = \text{arcsin}(A)-ft \Longleftrightarrow t =0, \text{arcsin}(A) \in [0, 2\pi) \\ \begin{cases} \theta < 0 \rightarrow \theta + 2\pi \\ \theta \geq0 \rightarrow \theta=\theta\end{cases}$$
He de decir que a $\theta$ se le suma $2\pi$ ya que $\text{arcsin}(\theta)$ se encuentra en el intervalo $[-\frac{\pi}{2}, \frac{\pi}{2}]$. **Tened esto a ojo que es importante**.

Paralelamente, suponiendo que $A=1=|\vec{\Delta r}|$ entonces
$a+bi = e^\theta$ teniendo esto: $$|\vec{\Delta r}|cos(\theta)+i|\vec{\Delta r}|cos(\theta)=e^\theta$$
Utilizando la Ley transitiva y simplificando, nos queda que $$cos(\theta)+isin(\theta)=e^\theta$$
Recalco nuevamente que $A=1=|\vec{\Delta r}|$. Es decir, $|\vec{\Delta r}|$ es una constante...

### Puntos ideales en M-PSK
Para modulaciones de tipo **M**-PSK $\rightarrow M=2^n \Longleftrightarrow n \in \mathbb{N}^+$ .
Un ángulo ideal $\theta$ equivaldría a: $$\theta_k=\frac{2\pi k}{M} \rightarrow k=0, 1, 2, ..., M-1$$
Por lo tanto: $$e^{i\theta_k}=cos(\frac{2\pi k}{M})+isin(\frac{2\pi k}{M})$$ O también: $$\pm a\pm bi \rightarrow a, b \in \{ 0, 1, 2, ..., \sqrt{M}-1\}$$
## Para M-QAM
Utilizamos la misma definición de onda senoidal, pero aquí $V \neq 1 \space , |\vec{\Delta r}| \neq 0, \theta \neq 0$. Como $Vsin(ft + \theta)=A$
Despejando: $$\theta = \text{arcsin}(\frac{A}{V}) \begin{cases} \text{Si }\theta < 0: \theta+2\pi \\ \text{Si }\theta \geq 0: \theta=\theta\end{cases}$$
También tenemos que $|\vec{\Delta r}|=a=\sqrt{(\Delta h)^2+1}$ . Donde $\Delta h$ es la diferencia entre una muestra y otra.

Esto nos quedaría como: $$Ae^{i\text{arcsin}(\theta)}=Acos(\theta)+isin(\theta)$$
### Puntos ideales en M-QAM
Esto es mucho mas simple y conlleva a mucha menos matemática:
$$\pm1 \pm1i, ..., \pm 2^{\frac{5M}{18}}\pm i2^{\frac{5M}{18}}$$
